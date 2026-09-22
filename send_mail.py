"""Aylık raporu e-posta olarak gönderir: yorum gövdede, Excel dosyası ekte.

Gönderim Gmail üzerinden yapılır. .env içinde şunlar olmalı:
    MAIL_FROM          gönderen adres (Gmail)
    MAIL_APP_PASSWORD  Google hesabından alınan 16 haneli uygulama şifresi
    MAIL_TO            alıcı adres (birden çok alıcı virgülle ayrılır)

Kullanım:
    python send_mail.py
"""
import argparse
import smtplib
from email.message import EmailMessage
from pathlib import Path

from excel_report import REPORT_DIR
from load import connect, settings
from excel_report import sql

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def latest(pattern):
    """reports/ altındaki en güncel dosyayı bulur."""
    files = sorted(REPORT_DIR.glob(pattern))
    if not files:
        raise SystemExit(f"Gönderilecek dosya yok: reports/{pattern}")
    return files[-1]


def main(year=None):
    config = settings()
    missing = [k for k in ("MAIL_FROM", "MAIL_APP_PASSWORD", "MAIL_TO") if not config.get(k)]
    if missing:
        raise SystemExit(f".env dosyasında eksik ayar: {', '.join(missing)}")

    with connect() as connection:
        year = year or sql(connection, "SELECT MAX(year) AS y FROM v_annual").y[0]
        months = sql(connection, """
            SELECT MAX(months_reported) AS m FROM v_annual
            WHERE source = 'balance' AND year = {year}""", year=year).m[0]

    excel = REPORT_DIR / f"rapor_{year}-{months:02d}.xlsx"
    comment = REPORT_DIR / f"yorum_{year}-{months:02d}.md"
    if not excel.exists():
        excel = latest("rapor_*.xlsx")
    if not comment.exists():
        comment = latest("yorum_*.md")

    mail = EmailMessage()
    mail["Subject"] = f"Hazine Nabzı — {year} bütçe gerçekleşme raporu ({months} aylık)"
    mail["From"] = config["MAIL_FROM"]
    mail["To"] = config["MAIL_TO"]
    mail.set_content(
        comment.read_text(encoding="utf-8")
        + "\n---\nBu e-posta Hazine Nabzı akışı tarafından otomatik üretildi.\n"
          "Ayrıntılı tablolar ekteki Excel dosyasında.\n"
    )
    mail.add_attachment(
        excel.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel.name,
    )

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(config["MAIL_FROM"], config["MAIL_APP_PASSWORD"])
        server.send_message(mail)

    print(f"Gönderildi: {config['MAIL_TO']}  ek: {excel.name}  gövde: {comment.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="gönderilecek raporun yılı")
    main(parser.parse_args().year)
