from datetime import datetime, timedelta

MAX_STALE_DAYS = 5

def is_stale(last_seen: str) -> bool:
    dt = datetime.fromisoformat(last_seen)
    return datetime.utcnow() - dt > timedelta(days=MAX_STALE_DAYS)
