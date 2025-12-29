from pathlib import Path
from datetime import datetime, timedelta

N_DAYS = 180
K_TOP5 = 30

def ai_should_delete(
    path: Path,
    *,
    last_read_days: int,
    in_universe: bool,
    in_recent_top5: bool,
    in_core_watch: bool,
    has_newer_version: bool
) -> bool:
    """
    全部成立才刪
    """

    if last_read_days <= N_DAYS:
        return False

    if in_universe:
        return False

    if in_recent_top5:
        return False

    if in_core_watch:
        return False

    if not has_newer_version:
        return False

    return True
