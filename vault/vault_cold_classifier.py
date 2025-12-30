from pathlib import Path
from datetime import datetime, timedelta

COLD_DAYS = 90
WARM_DAYS = 30


def classify(path: Path, meta: dict) -> str:
    """
    回傳：HOT / WARM / COLD
    """
    now = datetime.now()

    last_used = meta.get("last_used")
    if not last_used:
        return "HOT"

    last_used_time = datetime.fromisoformat(last_used)
    delta = now - last_used_time

    # 黑天鵝 / 人格資料永不刪
    if meta.get("protected"):
        return "HOT"

    if delta > timedelta(days=COLD_DAYS):
        return "COLD"

    if delta > timedelta(days=WARM_DAYS):
        return "WARM"

    return "HOT"
