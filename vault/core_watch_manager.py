from datetime import datetime
from pathlib import Path
import json

CORE_LIMIT = 7
DECAY_DAYS = 30

CORE_PATH = Path("E:/Quant-Vault/STOCK_DB/core_watch.json")
HISTORY_PATH = Path("E:/Quant-Vault/STOCK_DB/history_rank.json")

def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def decay_score(last_seen: str):
    days = (datetime.utcnow() - datetime.fromisoformat(last_seen)).days
    return max(0.3, 1 - days / DECAY_DAYS)

def update_core_watch(today_rank: list):
    """
    today_rank: [(symbol, score), ...] 已排序
    """
    core = load_json(CORE_PATH)
    history = load_json(HISTORY_PATH)

    updated = {}

    # 先保留舊 core（但有衰退）
    for sym, meta in core.items():
        updated[sym] = meta
        updated[sym]["weight"] *= decay_score(meta["last_seen"])

    # 補位（優先歷史 Top5，再來今日最熱）
    for sym, score in today_rank:
        if sym in updated:
            updated[sym]["last_seen"] = datetime.utcnow().isoformat()
            updated[sym]["weight"] = max(updated[sym]["weight"], score)
        elif len(updated) < CORE_LIMIT:
            updated[sym] = {
                "weight": score,
                "last_seen": datetime.utcnow().isoformat()
            }

    # 只保留前 CORE_LIMIT
    final = dict(
        sorted(updated.items(), key=lambda x: x[1]["weight"], reverse=True)[:CORE_LIMIT]
    )

    save_json(CORE_PATH, final)
    return final
