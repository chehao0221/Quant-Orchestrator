from pathlib import Path
import json

VAULT = Path("E:/Quant-Vault/LOCKED_RAW/backtest")

def read_last_n_days(market: str, days: int = 5):
    base = VAULT / market
    if not base.exists():
        return None

    files = sorted(base.glob("*.json"), reverse=True)
    records = []

    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        for r in data["symbols"].values():
            if r["hit"] is not None:
                records.append(r)
        if len(records) >= days:
            break

    if not records:
        return None

    total = len(records)
    wins = [r for r in records if r["hit"]]
    avg_ret = sum(r["actual_ret"] for r in records) / total
    max_dd = min(r["actual_ret"] for r in records)

    return {
        "trades": total,
        "hit_rate": round(len(wins) / total * 100, 1),
        "avg_ret": round(avg_ret * 100, 2),
        "max_dd": round(max_dd * 100, 2),
    }
