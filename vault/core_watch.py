import json
from datetime import datetime
from .resolver import path

MAX_CORE = 5
MIN_HIT_RATE = 0.45

def update_core_watch(market: str, performance: dict):
    """
    performance:
    {
      "2330": {"hit_rate":0.52, "count":30},
      ...
    }
    """
    p = path(market, "core_watch", "current.json")
    current = {}
    if os.path.exists(p):
        current = json.load(open(p, "r", encoding="utf-8"))

    merged = {**current, **performance}

    filtered = {
        k: v for k, v in merged.items()
        if v["hit_rate"] >= MIN_HIT_RATE
    }

    top = dict(
        sorted(filtered.items(), key=lambda x: x[1]["hit_rate"], reverse=True)[:MAX_CORE]
    )

    json.dump(top, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
