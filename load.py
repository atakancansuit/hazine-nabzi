"""data/clean/ altındaki tabloları SQL Server'a yükler.

Her çalıştığında tabloları sıfırlayıp yeniden doldurur: kaynak dosyalar her ay
güncellendiği için veritabanı da o anki halin tam kopyası olur.

Bağlantı bilgileri .env dosyasından okunur (bkz. .env.example).

Kullanım:
    python load.py
"""
from pathlib import Path

import pandas as pd
import pymssql

ROOT = Path(__file__).parent
CLEAN_DIR = ROOT / "data" / "clean"

# Tablo tanımları. Birincil anahtar aynı kalemin iki kez girmesini engelliyor:
# veri hatalı olsa yükleme hata verir, sessizce tekrar eden satır oluşmaz.
TABLES = {
    "actuals": """
        CREATE TABLE actuals (
            source              VARCHAR(20)    NOT NULL,
            year                SMALLINT       NOT NULL,
            month               TINYINT        NOT NULL,
            main_item           NVARCHAR(120)  NOT NULL,
            item                NVARCHAR(200)  NOT NULL,
            amount_thousand_try DECIMAL(19, 5) NOT NULL,
            CONSTRAINT pk_actuals PRIMARY KEY (source, year, month, item)
        )""",
    "plans": """
        CREATE TABLE plans (
            source              VARCHAR(20)    NOT NULL,
            year                SMALLINT       NOT NULL,
            main_item           NVARCHAR(120)  NOT NULL,
            item                NVARCHAR(200)  NOT NULL,
            amount_thousand_try DECIMAL(19, 5) NOT NULL,
            CONSTRAINT pk_plans PRIMARY KEY (source, year, item)
        )""",
}


def settings():
    """.env dosyasını okur."""
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def connect():
    """SQL Server bağlantısı açar."""
    config = settings()
    return pymssql.connect(
        server=config["DB_SERVER"], port=int(config["DB_PORT"]),
        user=config["DB_USER"], password=config["DB_PASSWORD"],
        database=config["DB_NAME"], login_timeout=10,
    )


def load_table(cursor, name, create_sql):
    """Tabloyu sıfırdan oluşturup ilgili CSV'yi içine yazar."""
    rows = pd.read_csv(CLEAN_DIR / f"{name}.csv")
    cursor.execute(f"DROP TABLE IF EXISTS {name}")
    cursor.execute(create_sql)
    columns = ", ".join(rows.columns)
    placeholders = ", ".join(["%s"] * len(rows.columns))
    cursor.executemany(f"INSERT INTO {name} ({columns}) VALUES ({placeholders})",
                       list(rows.itertuples(index=False, name=None)))
    return len(rows)


def main():
    with connect() as connection:
        cursor = connection.cursor()
        for name, create_sql in TABLES.items():
            written = load_table(cursor, name, create_sql)
            connection.commit()
            # Yazdığımız satır sayısı gerçekten tabloda mı? Birincil anahtar
            # yüzünden düşen satır olsaydı burada ortaya çıkardı.
            cursor.execute(f"SELECT COUNT(*) FROM {name}")
            stored = cursor.fetchone()[0]
            if stored != written:
                raise ValueError(f"{name}: {written} satır yazıldı ama tabloda {stored} var")
            print(f"{name:8s} {stored:,} satır")


if __name__ == "__main__":
    main()
