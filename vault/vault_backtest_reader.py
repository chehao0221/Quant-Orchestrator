from pathlib import Path
import json
from datetime import datetime, timedelta

VAULT_ROOT = Path("E:/Quant-Vault/LOCKED_RAW/backtest")

def read_recent_backtest(market: str, days: int = 5):
    market_dir = VAULT_ROOT / market
    if not market_dir.exists():
        return None

    files = sorted(market_dir.glob("*.json"), reverse=True)
    records = []

    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        for sym, r in data["symbols"].items():
            if r["hit"] is None:
                continue
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
        "hit_rate": len(wins) / total * 100,
        "avg_ret": avg_ret,
        "max_dd": max_dd
    }
