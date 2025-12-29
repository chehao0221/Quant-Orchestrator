from datetime import datetime

def ai_should_delete(meta: dict) -> bool:
    """
    必須「全部成立」才刪
    """

    # ---- 硬條件 ----
    if meta["last_access_days"] < 180:
        return False

    if meta.get("in_universe", False):
        return False

    if meta.get("in_recent_top5", False):
        return False

    if meta.get("in_core_watch", False):
        return False

    if not meta.get("has_newer_version", False):
        return False

    # ---- 隱性保險 ----
    if meta.get("read_by_ai_7d", False):
        return False

    if meta.get("top5_count", 0) >= 3:
        return False

    if meta.get("black_swan_related", False):
        return False

    return True
