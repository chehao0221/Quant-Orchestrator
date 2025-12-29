from datetime import datetime
from typing import List, Dict

DECAY_RATE = 0.98
MAX_CORE = 7
REPLACE_THRESHOLD = 0.4

def decay_core_score(stock: dict):
    if stock.get("is_black_swan"):
        return stock["core_score"]

    days = stock.get("days_since_active", 0)
    return stock["core_score"] * (DECAY_RATE ** days)


def update_core_watch(
    core_list: List[dict],
    explorer_candidates: List[dict]
) -> List[dict]:

    # 衰退
    for s in core_list:
        s["core_score"] = decay_core_score(s)

    # 可被替換者
    core_list = sorted(core_list, key=lambda x: x["core_score"], reverse=True)
    core_list = [s for s in core_list if s["core_score"] >= REPLACE_THRESHOLD]

    # 補位
    for c in explorer_candidates:
        if len(core_list) >= MAX_CORE:
            break
        if c["symbol"] not in {s["symbol"] for s in core_list}:
            c["is_core"] = True
            core_list.append(c)

    return core_list[:MAX_CORE]
