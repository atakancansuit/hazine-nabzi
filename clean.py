"""data/raw/ altındaki ham Excel dosyalarını temizleyip data/clean/ altına iki tablo yazar.

  actuals.csv  Aylık gerçekleşen tutarlar
               source, year, month, main_item, item, amount_thousand_try
  plans.csv    Yıl başındaki plan (başlangıç ödeneği)
               source, year, main_item, item, amount_thousand_try

`source` satırın hangi tablodan geldiğini söyler: balance, expense_detail, ministries.

Kullanım:
    python clean.py
"""
import re
from pathlib import Path

import pandas as pd

from xls_reader import read_xls

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"

# Ay adlarının ilk üç harfi. Bazı yıllarda aylar "Ocak", bazılarında "Oca" diye
# yazılmış; 2015'te Ağustos "Agu" olarak geçiyor.
MONTHS = {
    "oca": 1, "şub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6,
    "tem": 7, "ağu": 8, "agu": 8, "eyl": 9, "eki": 10, "kas": 11, "ara": 12,
}


# --- Yardımcı fonksiyonlar ---------------------------------------------------

def normalize(text):
    """Metindeki fazla boşlukları teke indirir, baştaki ve sondaki boşlukları atar."""
    return re.sub(r"\s+", " ", str(text)).strip()


def month_number(label):
    """'Ocak', 'Oca' ya da 'Agu' gibi bir ay adını 1-12 arası sayıya çevirir. Ay değilse None."""
    label = normalize(label).lower()
    if len(label) > 7:
        return None
    return MONTHS.get(label[:3])


def find_header_row(df):
    """Ay adlarının yazdığı satırın numarasını döndürür."""
    for i in range(len(df)):
        if any(month_number(v) == 1 for v in df.iloc[i]):
            return i
    raise ValueError("Ay başlıklarının olduğu satır bulunamadı")


def header_labels(df, row):
    """Başlık satırındaki sütun adlarını döndürür.

    Bazı tablolarda başlık iki satıra bölünmüş: aylar alt satırda, plan sütununun
    adı üst satırda. Bir sütunun adı alt satırda boşsa üst satırdaki ad kullanılır.
    """
    labels = []
    for col in range(df.shape[1]):
        label = df.iloc[row, col]
        if pd.isna(label) and row > 0:
            label = df.iloc[row - 1, col]
        labels.append("" if pd.isna(label) else normalize(label))
    return labels


def month_columns(labels):
    """{sütun numarası: ay numarası} sözlüğü döndürür."""
    return {col: month_number(label) for col, label in enumerate(labels) if month_number(label)}


def find_column(labels, *starts):
    """Adı verilen ifadelerden biriyle başlayan ilk sütunun numarasını döndürür.

    Sütunları sıralarıyla değil adlarıyla bulmak gerekiyor, çünkü bazı yıllarda
    fazladan sütun var ve sıralar kayıyor.
    """
    for col, label in enumerate(labels):
        if any(label.startswith(start) for start in starts):
            return col
    raise ValueError(f"Sütun bulunamadı: {starts}")


def find_plan_column(labels):
    """Yıl başındaki plan sütununun numarasını döndürür.

    Plan, Bütçe Kanunu'nda verilen başlangıç ödeneği. Sütunun adı tablodan tabloya
    ve yıldan yıla değişiyor: "2025 Bütçe Tahmini*", "Başlangıç Ödeneği",
    "Bütçe Başlangıç Ödeneği *", "Toplam Bütçe Ödeneği*", "Bütçe Ödeneği*".
    Kurumsal tablonun 2015-2024 yıllarındaki "Ödenek Toplamı" sütunu bilerek alınmıyor:
    o, yıl içindeki aktarımlardan sonraki güncel ödenek.
    """
    for col, label in enumerate(labels):
        if any(key in label for key in ("Bütçe Tahmin", "Başlangıç Ödeneği", "Bütçe Ödeneği")):
            return col
    raise ValueError("Plan sütunu bulunamadı")


def build_tables(records, year, source):
    """Okunan satırları iki tabloya çevirir: aylık gerçekleşen ve yıllık plan.

    records: her biri {"item", "main_item", "months": {ay: tutar}, "plan": tutar}
    olan satırların listesi.

    Boş hücre iki anlama geliyor ve ikisi ayrılıyor: bir ay tabloda herhangi bir
    kalemde doluysa o ay yayımlanmış sayılır ve boş hücreler "harcama yok" kabul
    edilip 0 yazılır (2022'de yedek ödenek satırının tamamı böyle boş). Hiçbir
    kalemde dolu olmayan aylar henüz yayımlanmamıştır ve tabloya girmez
    (2026'da Eylül ve sonrası).
    """
    published = {month for row in records for month, amount in row["months"].items()
                 if pd.notna(amount)}
    actuals = pd.DataFrame(
        {"source": source, "year": year, "month": month, "main_item": row["main_item"],
         "item": row["item"],
         "amount_thousand_try": 0.0 if pd.isna(amount) else amount}
        for row in records
        for month, amount in row["months"].items()
        if month in published
    )
    plans = pd.DataFrame(
        {"source": source, "year": year, "main_item": row["main_item"],
         "item": row["item"], "amount_thousand_try": row["plan"]}
        for row in records
        if pd.notna(row["plan"])
    )
    return actuals, plans


def open_table(path):
    """Bir ham dosyayı açar ve okumak için gereken her şeyi döndürür."""
    df = read_xls(path)
    header = find_header_row(df)
    labels = header_labels(df, header)
    return df, header, labels, month_columns(labels), find_plan_column(labels)


def row_values(df, row, months, plan_col, total_col):
    """Bir satırın aylık tutarlarını ve planını okur, ayların toplamını doğrular."""
    values = {month: pd.to_numeric(df.iloc[row, col], errors="coerce")
              for col, month in months.items()}
    plan = pd.to_numeric(df.iloc[row, plan_col], errors="coerce")
    total = pd.to_numeric(df.iloc[row, total_col], errors="coerce")
    months_sum = sum(v for v in values.values() if pd.notna(v))
    # Dosyanın kendi "Toplam" sütunu, ayların toplamını tutmalı. Kuruş farkına izin
    # var; büyük fark yanlış sütunu okuduğumuz anlamına gelir.
    if pd.notna(total) and abs(months_sum - total) > 1:
        raise ValueError(f"Ay toplamı tutmuyor: satır {row}, {months_sum} != {total}")
    return values, plan


def check_total_row(records, total, year, what):
    """Okunan satırların ayrı ayrı toplamı, tablonun kendi toplam satırına eşit mi?

    Bir satırı atlamış ya da iki kez okumuş olsaydık burada yakalanırdı.
    """
    if total is None:
        raise ValueError(f"{year}: toplam satırı bulunamadı ({what})")
    for month, expected in total.items():
        read = sum(row["months"][month] for row in records if pd.notna(row["months"][month]))
        if pd.notna(expected) and abs(read - expected) > 1:
            raise ValueError(f"{year}/{month}. ay: {what} toplamı tutmuyor, "
                             f"okunan {read:,.0f} != tablodaki {expected:,.0f}")


# --- Tablo okuyucular ----------------------------------------------------------

# Denge tablosunda kalemler üç bölümde sıralanıyor. Bölüm başlıkları bunlar.
BALANCE_SECTIONS = {"Harcamalar": "Harcamalar", "Gelirler": "Gelirler",
                    "Bütçe Dengesi": "Denge"}


def read_balance(year):
    """Bütçe denge tablosunu okur: gelir ve giderin ana kalemleri, bütçe dengesi."""
    df, header, labels, months, plan_col = open_table(RAW_DIR / f"{year}_balance.xls")
    total_col = find_column(labels, "Toplam")

    records, section = [], None
    for row in range(header + 1, len(df)):
        item = normalize(df.iloc[row, 1])
        values, plan = row_values(df, row, months, plan_col, total_col)
        # Dipnot satırlarında hiç sayı yok. Bir satırın ayları tamamen boş olabilir
        # (2022'de yedek ödenek hiç harcanmamış) ama planı varsa o bir kalemdir.
        if not item or (pd.isna(plan) and all(pd.isna(v) for v in values.values())):
            continue
        section = BALANCE_SECTIONS.get(item, section)
        records.append({"item": item, "main_item": section, "months": values, "plan": plan})

    return build_tables(records, year, "balance")


def read_expense_detail(year, items):
    """Gider detay tablosundan items.csv'de seçilen kalemleri okur."""
    df, header, labels, months, plan_col = open_table(RAW_DIR / f"{year}_expense_detail.xls")
    total_col = find_column(labels, "Toplam")
    names = [normalize(v) for v in df.iloc[:, 1]]

    records = []
    for item in items:
        # Aranan kalemin o yıldaki adı: 2021'de değişenler için eski ad da geçerli.
        wanted = {item["item"], item["old_name"]} - {""}
        # Bazı adlar tabloda birden çok kez geçiyor ("Memurlar" hem personel hem SGK
        # altında, "-Tahvil Faizi" biri boş iki yerde). search_under, kalemin hangi
        # başlığın altında aranacağını söylüyor.
        start = header + 1
        if item["search_under"]:
            if item["search_under"] not in names:
                raise ValueError(f"{year}: başlık bulunamadı: {item['search_under']}")
            start = names.index(item["search_under"]) + 1
        row = next((i for i in range(start, len(names)) if names[i] in wanted), None)
        if row is None:
            raise ValueError(f"{year}: kalem bulunamadı: {item['item']}")

        values, plan = row_values(df, row, months, plan_col, total_col)
        records.append({"item": item["item"], "main_item": item["main_item"],
                        "months": values, "plan": plan})

    return build_tables(records, year, "expense_detail")


def read_ministries(year):
    """Genel bütçeli kurumların (bakanlıklar, Meclis, Diyanet vb.) tablosunu okur."""
    df, header, labels, months, plan_col = open_table(RAW_DIR / f"{year}_ministries.xls")
    total_col = find_column(labels, "Toplam")

    records, total = [], None
    for row in range(header + 1, len(df)):
        # Kurum adlarının yazımı yıldan yıla değişiyor: "Hazine Ve Maliye" / "Hazine ve Maliye".
        name = normalize(df.iloc[row, 1]).replace(" Ve ", " ve ")
        values, plan = row_values(df, row, months, plan_col, total_col)
        if not name or (pd.isna(plan) and all(pd.isna(v) for v in values.values())):
            continue
        # "Genel Bütçeli İdareler" satırı kurum listesini bitirir: toplamdır. Bazı
        # yıllarda altında özel bütçeli idareler, düzenleyici kurumlar ve merkezi
        # yönetim toplamı gibi özet satırları da var; onlar bu tablonun konusu değil.
        if name.startswith("Genel Bütçeli İdareler"):
            total = values
            break
        records.append({"item": name, "main_item": "Genel Bütçeli İdareler",
                        "months": values, "plan": plan})

    check_total_row(records, total, year, "kurum")
    return build_tables(records, year, "ministries")


# --- Ana akış ------------------------------------------------------------------

# Aynı kalem iki tabloda farklı adla yazılmış. Mutabakat bu eşleşmeye göre yapılıyor.
DETAIL_TO_BALANCE = {
    "1. Personel Giderleri": "Personel Giderleri",
    "2. Sosyal Güvenlik Kurumlarına Devlet Primi Giderleri": "Sosyal Güv.Kur. Devlet Primi",
    "3. Mal ve Hizmet Alım Giderleri": "Mal ve Hizmet Alımları",
    "4. Cari Transferler": "Cari Transferler",
    "5. Sermaye Giderleri": "Sermaye Giderleri",
    "6. Sermaye Transferleri": "Sermaye Transferleri",
    "7. Borç Verme": "Borç Verme",
    "8. Yedek Ödenekler": "Yedek Ödenekler",
    "B. Faiz Giderleri": "2-Faiz Harcamaları",
}


def reconcile(table):
    """Gider detayındaki ana kalemler, denge tablosundaki aynı kalemlere eşit mi?

    İki tablo birbirinden bağımsız yayımlanıyor. Aynı kalemin iki tabloda aynı
    tutarı vermesi, doğru satırları ve doğru sütunları okuduğumuzun kanıtı.
    """
    detail = table[table["source"] == "expense_detail"].copy()
    detail = detail[detail["item"].isin(DETAIL_TO_BALANCE)]
    detail["item"] = detail["item"].map(DETAIL_TO_BALANCE)
    balance = table[table["source"] == "balance"]

    keys = [c for c in ("year", "month", "item") if c in table.columns]
    merged = detail.merge(balance, on=keys, suffixes=("_detail", "_balance"))
    expected = len(detail)
    if len(merged) != expected:
        raise ValueError(f"Mutabakat: {expected} satır beklenirken {len(merged)} eşleşti")

    diff = (merged["amount_thousand_try_detail"] - merged["amount_thousand_try_balance"]).abs()
    if (diff > 1).any():
        worst = merged.loc[diff.idxmax()]
        raise ValueError(f"Mutabakat tutmadı: {worst['year']} {worst['item']} "
                         f"fark {diff.max():,.0f} bin TL")
    return len(merged)


def load_items():
    """items.csv'yi okur: gider detayından alınacak kalemler."""
    return pd.read_csv(ROOT / "items.csv").fillna("").to_dict("records")


def main():
    items = load_items()
    years = sorted({int(path.name[:4]) for path in RAW_DIR.glob("*_balance.xls")})

    actuals, plans = [], []
    for year in years:
        for table, plan in (read_balance(year), read_expense_detail(year, items),
                            read_ministries(year)):
            actuals.append(table)
            plans.append(plan)
    actuals = pd.concat(actuals, ignore_index=True)
    plans = pd.concat(plans, ignore_index=True)

    checked = reconcile(actuals) + reconcile(plans)
    print(f"Mutabakat: gider detayı ile denge tablosu {checked:,} noktada karşılaştırıldı, "
          f"hepsi tuttu.")

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    actuals.to_csv(CLEAN_DIR / "actuals.csv", index=False)
    plans.to_csv(CLEAN_DIR / "plans.csv", index=False)
    print(f"{years[0]}-{years[-1]}  actuals.csv {len(actuals):,} satır  "
          f"plans.csv {len(plans):,} satır")


if __name__ == "__main__":
    main()
