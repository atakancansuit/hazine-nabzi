"""Ayın rakamlarından kısa bir yönetim yorumu yazdırır.

Rakamları veritabanından alır, tek bir metin haline getirir ve Claude'a
yorumlatır. Model hesap yapmaz; yalnızca verilen rakamları cümleye çevirir.
Yorum reports/yorum_<yıl>-<ay>.md dosyasına yazılır.

Çalışması için .env içinde ANTHROPIC_API_KEY olmalı.

Kullanım:
    python commentary.py
    python commentary.py --year 2025
"""
import argparse
from pathlib import Path

import anthropic

from excel_report import REPORT_DIR, sql
from load import connect, settings

MODEL = "claude-opus-5"

SYSTEM = """Sen bir kamu maliyesi analistisin. Sana verilen bütçe rakamlarından
yöneticilere okunacak kısa bir aylık yorum yazıyorsun.

Kurallar:
- Yalnızca sana verilen rakamları kullan. Veride olmayan bir sayı, sebep ya da
  olay uydurma. Bir şeyin sebebini bilmiyorsan sebep yazma, olguyu yaz.
- En fazla dört kısa paragraf. Her paragraf tek bir konuya odaklansın.
- Sade Türkçe kullan. Süslü ifade, benzetme ve giriş cümlesi yok; doğrudan bulguya gir.
- Tutarları milyar TL olarak, yüzdeleri tek ondalıkla yaz.
- Yıl bitmemişse bunu belirt ve yıl sonu tahminini "tahmin" olarak ver.
- Tahminin geçmişteki hata payını da bir kez söyle ki okuyan ne kadar güveneceğini bilsin.
"""


def facts(connection, year):
    """Modele verilecek rakamları tek bir metin haline getirir."""
    months = sql(connection, """
        SELECT MAX(months_reported) AS m FROM v_annual
        WHERE source = 'balance' AND year = {year}""", year=year).m[0]

    ana = sql(connection, """
        SELECT d.display_name AS kalem,
               CAST(a.actual / 1e6 AS DECIMAL(10,0))   AS gerceklesen,
               CAST(a.planned / 1e6 AS DECIMAL(10,0))  AS planlanan,
               CAST(a.pct_of_plan AS DECIMAL(5,1))     AS oran,
               CAST(m.typical_pct_of_plan AS DECIMAL(5,1)) AS kiyas,
               CAST(f.forecast_pct_of_plan AS DECIMAL(5,1)) AS tahmin
        FROM v_annual a
        JOIN dim_item d ON d.item_key = a.item_key
        LEFT JOIN v_monthly m ON m.item_key = a.item_key AND m.year = a.year AND m.month = {months}
        LEFT JOIN v_year_end_forecast f ON f.item_key = a.item_key AND f.year = a.year
        WHERE a.source = 'balance' AND a.year = {year}
        ORDER BY a.actual DESC""", year=year, months=months)

    kalem = sql(connection, """
        SELECT TOP 8 d.display_name AS kalem,
               CAST(a.actual / 1e6 AS DECIMAL(10,0))  AS gerceklesen,
               CAST(a.planned / 1e6 AS DECIMAL(10,0)) AS planlanan,
               CAST(a.pct_of_plan AS DECIMAL(5,1))    AS oran
        FROM v_annual a
        JOIN dim_item d ON d.item_key = a.item_key
        WHERE a.source = 'expense_detail' AND a.year = {year} AND d.is_total = 0
        ORDER BY ABS(a.variance) DESC""", year=year)

    kurum = sql(connection, """
        SELECT TOP 5 d.display_name AS kurum,
               CAST(a.actual / 1e6 AS DECIMAL(10,0))  AS gerceklesen,
               CAST(a.planned / 1e6 AS DECIMAL(10,0)) AS planlanan,
               CAST(a.pct_of_plan AS DECIMAL(6,1))    AS oran
        FROM v_annual a
        JOIN dim_item d ON d.item_key = a.item_key
        WHERE a.source = 'ministries' AND a.year = {year}
        ORDER BY ABS(a.variance) DESC""", year=year)

    hata = sql(connection, """
        SELECT DISTINCT CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY error_pct)
               OVER (PARTITION BY month) AS DECIMAL(5,1)) AS medyan_hata
        FROM v_forecast_backtest
        WHERE source = 'balance' AND month = {months}""", months=months).medyan_hata[0]

    return months, (
        f"Yıl: {year}. Yayımlanmış ay sayısı: {months} (12 ise yıl tamamlanmıştır).\n"
        f"Tutarlar milyar TL. 'oran' = gerçekleşenin yıllık plana oranı, yüzde.\n"
        f"'kiyas' = geçmiş yıllarda aynı ayda planın yüzde kaçı gerçekleşmişti.\n"
        f"'tahmin' = bu gidişle yıl sonunda plana göre nerede olunacağı, yüzde.\n\n"
        f"ANA KALEMLER\n{ana.to_string(index=False)}\n\n"
        f"SAPMASI EN BÜYÜK GİDER KALEMLERİ\n{kalem.to_string(index=False)}\n\n"
        f"SAPMASI EN BÜYÜK KURUMLAR\n{kurum.to_string(index=False)}\n\n"
        f"Yıl sonu tahmin yönteminin {months} aylık veriyle geçmişteki medyan hatası: %{hata}."
    )


def main(year=None):
    """Yorumu üretir ve dosyaya yazar; dosyanın yolunu döndürür."""
    api_key = settings().get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(".env dosyasında ANTHROPIC_API_KEY yok")

    with connect() as connection:
        year = year or sql(connection, "SELECT MAX(year) AS y FROM v_annual").y[0]
        months, veri = facts(connection, year)

    response = anthropic.Anthropic(api_key=api_key).messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM,
        output_config={"effort": "low"},  # kısa bir özet için derin düşünmeye gerek yok
        messages=[{"role": "user", "content":
                   f"Aşağıdaki rakamlardan aylık yönetim yorumunu yaz.\n\n{veri}"}],
    )
    text = "\n".join(block.text for block in response.content if block.type == "text")

    REPORT_DIR.mkdir(exist_ok=True)
    path = REPORT_DIR / f"yorum_{year}-{months:02d}.md"
    path.write_text(text.strip() + "\n", encoding="utf-8")

    usage = response.usage
    print(f"{path.name}  ({len(text.split())} kelime, "
          f"{usage.input_tokens} girdi + {usage.output_tokens} çıktı jetonu)")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="yorumlanacak yıl (varsayılan: en güncel yıl)")
    main(parser.parse_args().year)
