# 日股 Explorer 股池更新器（封頂最終版）
# 僅負責：建立 / 更新 universe、shortlist、core_watch 的資料快照
# ❌ 不交易 ❌ 不做風控 ❌ 不寫 LOCKED_*

import os
import json
from datetime import datetime
from typing import List, Dict

VAULT_ROOT = r"E:\Quant-Vault"
BASE_DIR = os.path.join(VAULT_ROOT, "STOCK_DB", "JP")

UNIVERSE_DIR = os.path.join(BASE_DIR, "universe")
SHORTLIST_DIR = os.path.join(BASE_DIR, "shortlist")
CORE_WATCH_DIR = os.path.join(BASE_DIR, "core_watch")

for d in (UNIVERSE_DIR, SHORTLIST_DIR, CORE_WATCH_DIR):
    os.makedirs(d, exist_ok=True)


def fetch_market_universe() -> List[Dict]:
    """
    取得日股全市場候選（示意）
    真實來源可接：你既有 safe_yfinance / 外部資料
    無資料 → 回傳空陣列（上層會停止）
    """
    return []  # 尚未初始化資料層，保持安全行為


def rank_and_select(universe: List[Dict]) -> Dict[str, List[Dict]]:
    """
    排序並選擇：
    - shortlist：Top 5
    - core_watch：<= 7（示意，實務可接穩定度/衰退權重）
    """
    if not universe:
        return {"shortlist": [], "core_watch": []}

    sorted_items = universe[:]
    return {
        "shortlist": sorted_items[:5],
        "core_watch": sorted_items[:7],
    }


def write_snapshot(folder: str, name: str, data):
    path = os.path.join(folder, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    universe = fetch_market_universe()
    if not universe:
        # 無資料 → 不寫任何東西（避免假資料）
        return

    ranked = rank_and_select(universe)
    ts = datetime.utcnow().strftime("%Y%m%d")

    write_snapshot(UNIVERSE_DIR, f"universe_{ts}", universe)
    write_snapshot(SHORTLIST_DIR, f"shortlist_{ts}", ranked["shortlist"])
    write_snapshot(CORE_WATCH_DIR, f"core_watch_{ts}", ranked["core_watch"])


if __name__ == "__main__":
    main()
