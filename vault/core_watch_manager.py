import json
from pathlib import Path
from datetime import date, datetime, timedelta

VAULT_DIR = Path(__file__).resolve().parents[1] / "vault_data"
VAULT_DIR.mkdir(exist_ok=True)

DECAY_DAYS = 14          # 衰退半衰期
MAX_CORE = 7             # 固定標最多 7 檔


def _decay(weight: float, days: int) -> float:
    return weight * (0.5 ** (days / DECAY_DAYS))


def load_core(market: str) -> list:
    path = VAULT_DIR / f"core_watch_{market.lower()}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_core(market: str, core: list):
    path = VAULT_DIR / f"core_watch_{market.lower()}.json"
    path.write_text(json.dumps(core, ensure_ascii=False, indent=2))


def update_core_watch(
    market: str,
    today_hits: list[str],
    explorer_hits: list[str]
):
    """
    today_hits     → 今天實際進入核心顯示的股票
    explorer_hits  → 今日 Top5 / Explorer 命中
    """

    today = date.today()
    core = load_core(market)
    core_map = {c["symbol"]: c for c in core}

    # 1️⃣ 先對所有既有核心做衰退
    for c in core:
        last = datetime.strptime(c["last_active"], "%Y-%m-%d").date()
        days = (today - last).days
        c["weight"] = round(_decay(c["weight"], days), 4)

    # 2️⃣ 今日命中 → 加權
    for sym in set(today_hits + explorer_hits):
        if sym not in core_map:
            core_map[sym] = {
                "symbol": sym,
                "market": market,
                "weight": 1.0,
                "hit_count": 1,
                "miss_count": 0,
                "last_active": today.isoformat(),
            }
        else:
            core_map[sym]["weight"] += 1.0
            core_map[sym]["hit_count"] += 1
            core_map[sym]["last_active"] = today.isoformat()

    # 3️⃣ 未命中者 miss +1
    for c in core_map.values():
        if c["symbol"] not in today_hits:
            c["miss_count"] += 1

    # 4️⃣ 依權重排序，只留前 MAX_CORE
    new_core = sorted(
        core_map.values(),
        key=lambda x: x["weight"],
        reverse=True
    )[:MAX_CORE]

    save_core(market, new_core)
    return new_core
