"""sql/ klasöründeki görünümleri ve yordamları veritabanına uygular.

Dosyalar GO satırlarıyla bölünüp sırayla çalıştırılır. Her nesne CREATE OR ALTER
ile yazıldığı için betik istendiği kadar tekrar çalıştırılabilir.

Kullanım:
    python apply_sql.py
"""
import re
from pathlib import Path

from load import connect

SQL_DIR = Path(__file__).parent / "sql"
FILES = ["views.sql", "procedures.sql"]


def statements(text):
    """Dosyayı GO satırlarından bölerek tek tek çalıştırılacak parçalara ayırır."""
    for part in re.split(r"(?im)^\s*GO\s*$", text):
        if part.strip():
            yield part


def main():
    with connect() as connection:
        cursor = connection.cursor()
        for name in FILES:
            applied = 0
            for statement in statements((SQL_DIR / name).read_text(encoding="utf-8")):
                cursor.execute(statement)
                applied += 1
            connection.commit()
            print(f"{name:16s} {applied} nesne")

        cursor.execute("""
            SELECT type_desc, name FROM sys.objects
            WHERE type IN ('V', 'P') ORDER BY type_desc, name
        """)
        for kind, name in cursor.fetchall():
            print(f"  {kind:20s} {name}")


if __name__ == "__main__":
    main()
