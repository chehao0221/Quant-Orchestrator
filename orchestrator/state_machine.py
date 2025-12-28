from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))

def now():
    return datetime.now(TZ)

def enter_l4(state, hours=24, reason="black_swan"):
    t = now()
    state["risk_level"] = 4
    state["l4"]["active"] = True
    state["l4"]["since"] = t.isoformat()
    state["l4"]["pause_until"] = (t + timedelta(hours=hours)).isoformat()
    state["cooldown"]["active"] = False
    return state

def exit_l4(state):
    t = now()
    state["l4"]["active"] = False
    state["l4"]["last_end"] = t.isoformat()
    state["cooldown"]["active"] = True
    state["cooldown"]["until"] = (t + timedelta(hours=12)).isoformat()
    state["risk_level"] = 2
    return state
