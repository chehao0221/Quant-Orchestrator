from datetime import datetime, time

def is_quiet_hours() -> bool:
    now = datetime.now().time()
    return now >= time(21, 0) or now < time(8, 0)
