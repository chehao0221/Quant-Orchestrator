from datetime import datetime, timedelta

def is_cold(mtime, days: int):
    return datetime.now() - mtime > timedelta(days=days)
