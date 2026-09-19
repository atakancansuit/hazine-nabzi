"""Muhasebat Genel Müdürlüğü'nden merkezi yönetim bütçe tablolarını indirir.

Her yıl için üç dosya iner ve data/raw/ altına kaydedilir:
  <yıl>_balance.xls         Konsolide bütçe denge tablosu: ana kalemlerde plan ve aylık gerçekleşme
  <yıl>_expense_detail.xls  Giderlerin aylık detayı: alt kalemlerde plan ve gerçekleşme
  <yıl>_ministries.xls      Genel bütçeli kurumların (bakanlıklar vb.) aylık harcaması ve planı

Kullanım:
    python download.py
"""
import io
import re
from pathlib import Path

import requests

from xls_reader import read_xls

API = "https://muhasebat.hmb.gov.tr/portal/v2"
PAGE_SLUG = "merkezi-yonetim-butce-istatistikleri"
FIRST_YEAR = 2015
RAW_DIR = Path(__file__).parent / "data" / "raw"

# Her dosya türü için:
#   section: sitede hangi menü başlığının altında durduğu
#   name:    dosya adının ayırt edici kısmı. Türkçe karakterli ve karaktersiz
#            yazımlar yıllara göre değiştiği için ikisi de kabul edilir.
#   title:   dosya adı yetmediğinde, dosyanın içindeki başlıkta aranan ifade.
#            Kurumsal tabloların üçü (genel, özel, düzenleyici) aynı adı taşıyor.
FILES = {
    "balance": {
        "section": "Bütçe Dengesi",
        "name": re.compile(r"Merkezi-Y[oö]netim-Konsolide-B[uü]t[cç]e-Denge-Tablosu(?![-_]([ÖO]nceki|YEP))"),
    },
    "expense_detail": {
        "section": "Bütçe Gider",
        "name": re.compile(r"Merkezi-Y[oö]netim-B[uü]t[cç]e-Giderleri-Ay-[İI][cç]i-Ger[cç]ekle[sş]meleri-Detay2"),
    },
    "ministries": {
        "section": "Bütçe Gider",
        "name": re.compile(r"Kurulu[sş]-Baz[ıi]nda-[ÖO]denek-ve-Harcamalar-Tablosu"),
        "title": "GENEL BÜTÇELİ İDARELERİN",
    },
}

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"


def list_sections():
    """Sayfanın menüsünden (yıl, başlık, menü id) üçlülerini çıkarır."""
    page = session.get(f"{API}/pages", params={"slug": PAGE_SLUG}, timeout=30).json()[0]
    html = page["content"]["rendered"]
    year = None
    # Başlık olduğu gibi döndürülür: bazılarının başında boşluk var ve API
    # başlığı birebir istiyor. Karşılaştırmalarda .strip() kullanılır.
    for name, menu_id in re.findall(r'data-name="([^"]+)" data-id="(\d+)"', html):
        heading = re.match(r"(\d{4}) ", name.strip())
        if heading:
            year = int(heading.group(1))
        elif year:
            yield year, name, menu_id


def list_files(name, menu_id):
    """Bir menü başlığının altındaki dosyaların linklerini döndürür."""
    response = session.get(f"{API}/files", params={"name": name, "id": menu_id}, timeout=30).json()
    if not isinstance(response, dict):
        return []
    return re.findall(r'href="([^"]+\.xls)"', response["content"])


def title_of(content):
    """Dosyanın ilk satırlarındaki başlığı büyük harfle döndürür."""
    top = read_xls(io.BytesIO(content)).head(4)
    return " ".join(str(v) for v in top.values.ravel() if isinstance(v, str)).upper()


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    found = {}
    for year, name, menu_id in list_sections():
        if year < FIRST_YEAR:
            continue
        for kind, spec in FILES.items():
            if not name.strip().startswith(spec["section"]) or (year, kind) in found:
                continue
            for url in list_files(name, menu_id):
                if not spec["name"].search(url.rsplit("/", 1)[-1]):
                    continue
                content = session.get(url, timeout=60).content
                if "title" in spec and spec["title"] not in title_of(content):
                    continue
                found[(year, kind)] = content
                break

    for (year, kind), content in sorted(found.items()):
        path = RAW_DIR / f"{year}_{kind}.xls"
        path.write_bytes(content)
        print(f"{path.name:28s} {len(content) / 1024:6.0f} KB")

    years = range(FIRST_YEAR, max(y for y, _ in found) + 1)
    missing = [f"{y}_{k}" for y in years for k in FILES if (y, k) not in found]
    print(f"\n{len(found)} dosya indirildi.", f"Eksik: {missing}" if missing else "Eksik yok.")


if __name__ == "__main__":
    main()
