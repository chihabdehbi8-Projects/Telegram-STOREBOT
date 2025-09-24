# ================== sheet.py ==================
import pandas as pd

CATEGORY_KEYWORDS = {
    "LCD": "LCD",
    "Battery": "BATTERIE",
    "Connector": "CC",
    "Glass": "GLASS"
}

class SheetHandler:
    def __init__(self, csv_path='Article.csv'):
        self.csv_path = csv_path

    async def get_inventory(self):
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8', delimiter=',', low_memory=False)
        except Exception as e:
            print(f"[ERROR] Failed to read CSV file '{self.csv_path}': {e}")
            return []

        # Drop rows where Designation1 is missing
        if "Designation1" not in df.columns or "PU" not in df.columns or "QT" not in df.columns:
            print("[ERROR] Required columns not found in CSV")
            return []

        df = df.dropna(subset=["Designation1"])

        inventory = []
        for _, row in df.iterrows():
            inventory.append({
                "Designation1": str(row["Designation1"]).strip(),
                "PU": str(row["PU"]).strip(),
                "QT": str(row["QT"]).strip()
            })

        return inventory


sheet_handler = SheetHandler()
