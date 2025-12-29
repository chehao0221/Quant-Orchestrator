from .vault_backtest_reader import read_recent_backtest


def validate_backtest(market: str) -> dict:
    records = read_recent_backtest(market, days=5)
    if not records:
        return {
            "status": "NO_DATA",
            "hit_rate": 0.0,
            "avg_ret": 0.0,
        }

    hits = [r for r in records if r["hit"]]
    avg_ret = sum(r["actual_ret"] for r in records) / len(records)

    return {
        "status": "OK",
        "hit_rate": len(hits) / len(records),
        "avg_ret": avg_ret,
    }
