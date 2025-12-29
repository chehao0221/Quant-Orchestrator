from pathlib import Path
from datetime import datetime, timedelta

COLD_DAYS = 180
INSURANCE_DAYS = 7

def ai_should_delete(file_path: Path, last_read_days: int, top5_count: int) -> bool:
    if not file_path.is_file():
        return False

    age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days

    if age_days < COLD_DAYS:
        return False

    if last_read_days <= INSURANCE_DAYS:
        return False

    if top5_count >= 3:
        return False

    return True
