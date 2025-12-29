def summarize(records: list):
    if not records:
        return None

    wins = [r for r in records if r["pred_ret"] > 0]
    return {
        "count": len(records),
        "hit_rate": len(wins) / len(records),
        "avg_ret": sum(r["pred_ret"] for r in records) / len(records),
        "max_dd": min(r["pred_ret"] for r in records),
    }
