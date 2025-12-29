from pathlib import Path
from datetime import datetime, timedelta

MAX_AGE_DAYS = 7   # 你要改，只改這裡

def ai_should_delete(file_path: Path) -> bool:
    """
    極保守 AI：
    - 只看時間
    - 不看內容
    - 不做學習
    """

    if not file_path.is_file():
        return False

    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime

    return age > timedelta(days=MAX_AGE_DAYS)
