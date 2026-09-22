"""Bütün akışı tek komutla çalıştırır: indir → temizle → yükle → hesapla → raporla.

Her adımın çıktısı hem ekrana hem logs/<tarih>.log dosyasına yazılır. Bir adım
hata verirse akış orada durur: bozuk veri bir sonraki adıma geçmez.

Kullanım:
    python run.py
    python run.py --skip-download    # elindeki ham dosyalarla çalış
"""
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import apply_sql
import clean
import download
import excel_report
import load

ROOT = Path(__file__).parent
LOG_DIR = ROOT / "logs"

STEPS = [
    ("İndirme", download.main),
    ("Temizlik", clean.main),
    ("Yükleme", load.main),
    ("Hesaplar", apply_sql.main),
    ("Excel raporu", excel_report.main),
]


class Tee:
    """Yazılanı hem ekrana hem log dosyasına geçirir."""

    def __init__(self, log_file):
        self.terminal = sys.__stdout__
        self.log_file = log_file

    def write(self, text):
        self.terminal.write(text)
        self.log_file.write(text)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()


def run(steps):
    """Adımları sırayla çalıştırır, her birinin süresini yazar."""
    durations = []
    for name, step in steps:
        print(f"\n--- {name} ---", flush=True)
        started = time.perf_counter()
        step()
        durations.append((name, time.perf_counter() - started))

    print("\n--- Özet ---")
    for name, seconds in durations:
        print(f"{name:10s} {seconds:6.1f} sn")
    print(f"{'Toplam':10s} {sum(s for _, s in durations):6.1f} sn")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-download", action="store_true",
                        help="indirme adımını atla, data/raw altındaki dosyaları kullan")
    args = parser.parse_args()

    steps = [s for s in STEPS if not (args.skip_download and s[0] == "İndirme")]

    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"
    with log_path.open("a", encoding="utf-8") as log_file:
        sys.stdout = Tee(log_file)
        print(f"\n{'=' * 60}\nHazine Nabzı — {datetime.now():%d.%m.%Y %H:%M}")
        try:
            run(steps)
        except Exception as error:
            # Zamanlayıcıdan çalıştığında kimse ekrana bakmıyor: hata log dosyasına
            # yazılır ve sıfırdan farklı bir çıkış koduyla bitilir.
            print(f"\nHATA: {error}")
            sys.stdout = sys.__stdout__
            raise SystemExit(1)
        finally:
            sys.stdout = sys.__stdout__
    print(f"\nKayıt: {log_path}")


if __name__ == "__main__":
    main()
