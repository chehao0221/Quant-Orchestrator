def is_ai_trusted(perf: dict) -> bool:
    return (
        perf.get("hit_rate", 0) >= 0.60 and
        perf.get("samples", 0) >= 50
    )
