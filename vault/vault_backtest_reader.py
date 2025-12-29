from pathlib import Path
import json
from datetime import datetime

def load_history(
    market: str,
    days: int = 5,
):
    """
    market: 'TW' | 'US'
    days: 取最近 N 個交易日
    """
    root = Path(f"E:/Quant-Vault/STOCK_DB/{market}/history")
    if not root.exists():
        return []

    files = sorted(root.glob("*.json"))
    files = files[-days:]

    records = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            date = f.stem
            for r in data:
                r["_date"] = date
                records.append(r)
        except Exception:
            continue

    return records
