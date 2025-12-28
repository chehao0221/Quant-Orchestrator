from datetime import datetime, timezone, timedelta

# =========================
# Time
# =========================
TZ = timezone(timedelta(hours=8))

def now_ts():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M (UTC+8)")

# =========================
# Discord Colors
# =========================
COLOR_GREEN  = 0x2ECC71   # L1–L2（隱藏）
COLOR_YELLOW = 0xF1C40F   # L3
COLOR_RED    = 0xE74C3C   # L4+

# =========================
# Risk Policy（唯一決策表）
# =========================
def resolve_risk(level: int):
    if level <= 2:
        return {
            "show": False,
            "color": COLOR_GREEN,
            "action": "RUN_AI"
        }

    if level == 3:
        return {
            "show": True,
            "color": COLOR_YELLOW,
            "action": "RUN_AI_WITH_WARNING"
        }

    return {
        "show": True,
        "color": COLOR_RED,
        "action": "STOP_AI"
    }
