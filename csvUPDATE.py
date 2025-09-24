import subprocess
import time
import shutil

MDB_FILE = "Detail.mdb"
CSV_FILE = "Article.csv"
TABLE_NAME = "Article"
EXPORT_INTERVAL_SECONDS = 180  # 3 minutes

def export_articles():
    try:
        print("Exporting Articles table...")
        result = subprocess.run(
            ["mdb-export", MDB_FILE, TABLE_NAME],
            check=True,
            capture_output=True,
            text=True
        )
        with open(CSV_FILE, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        print("Articles table exported successfully.")
    except subprocess.CalledProcessError as e:
        print("Error exporting table:", e.stderr)

if __name__ == "__main__":
    while True:
        export_articles()
        time.sleep(EXPORT_INTERVAL_SECONDS)

