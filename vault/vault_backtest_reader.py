from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import List, Dict


# ==================================================
# Vault Backtest Reader
# ==================================================
# 職責：
# - 只讀 Vault
# - 不判斷風控
# - 不刪資料
# - 不猜不存在的欄位
# ==================================================


def _is_date_filename(name: str) -> bool:
    try:
        datetime.strptime(name.replace(".json", ""), "%Y-%m-%d")
        return True
    except Exception:
        return False


def load_history(
    market_root: Path,
    days: int = 5
) -> List[Dict]:
    """
    從 Vault history 讀取最近 N 天資料

    market_root:
        E:/Quant-Vault/STOCK_DB/TW
        E:/Quant-Vault/STOCK_DB/US

    回傳：
        List[{
            "date": "YYYY-MM-DD",
            "symbol": str,
            "pred": float
        }]
    """

    history_dir = market_root / "history"
    if not history_dir.exists():
        return []

    today = datetime.now().date()
    start_date = today - timedelta(days=days * 2)  # buffer 避開假日

    records: List[Dict] = []

    for file in sorted(history_dir.iterdir(), reverse=True):
        if not file.name.endswith(".json"):
            continue
        if not _is_date_filename(file.name):
            continue

        file_date = datetime.strptime(
            file.name.replace(".json", ""), "%Y-%m-%d"
        ).date()

        if file_date < start_date:
            break

        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue

        for item in data:
            if "pred" not in item or "symbol" not in item:
                continue

            records.append({
                "date": file_date.isoformat(),
                "symbol": item["symbol"],
                "pred": float(item["pred"])
            })

        if len({r["date"] for r in records}) >= days:
            break

    return records


def summarize_backtest(records: List[Dict]) -> Dict | None:
    """
    根據 Vault 歷史資料做「觀測性摘要」
    ❗ 不是真實損益
    ❗ 不假設實際交易
    """

    if not records:
        return None

    preds = [r["pred"] for r in records]

    win = [p for p in preds if p > 0]

    return {
        "count": len(preds),
        "win_rate": round(len(win) / len(preds) * 100, 1),
        "avg_pred": round(sum(preds) / len(preds), 4),
        "max_drawdown": round(min(preds), 4),
    }
