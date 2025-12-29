from datetime import datetime, timedelta

COLD_DAYS = 180

def ai_should_delete(meta: dict) -> bool:
    """
    meta = {
      "last_read": datetime,
      "is_in_universe": bool,
      "is_in_top5": bool,
      "is_in_core": bool,
      "has_newer": bool
    }
    """

    if meta["is_in_top5"]:
        return False

    if meta["is_in_core"]:
        return False

    if not meta["has_newer"]:
        return False

    if datetime.now() - meta["last_read"] < timedelta(days=COLD_DAYS):
        return False

    return True
