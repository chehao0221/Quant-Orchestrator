from datetime import datetime, timedelta

L4_RECHECK_MINUTES = 90

def transition(prev_state: dict, new_level: int) -> dict:
    now = datetime.utcnow().isoformat() + "Z"

    new_state = prev_state.copy()
    new_state["risk_level"] = new_level
    new_state["last_transition"] = now
    new_state["source"] = "Guardian"

    if new_level <= 2:
        new_state["risk_color"] = "GREEN"
        new_state["risk_label"] = "STABLE"
        new_state["l4_active"] = False

    elif new_level == 3:
        new_state["risk_color"] = "YELLOW"
        new_state["risk_label"] = "WARNING"
        new_state["l4_active"] = False

    elif new_level == 4:
        new_state["risk_color"] = "RED"
        new_state["risk_label"] = "DEFENSE"
        new_state["l4_active"] = True
        new_state["l4_last_check"] = now

    return new_state


def should_notify(prev_state: dict, new_state: dict) -> bool:
    """
    是否需要對外通知（避免洗頻）
    規則：
    - 紅 / 黃 進入時要發
    - 紅 → 綠 要發
    - 黃 → 綠 要發
    - 其餘靜默
    """
    if prev_state["risk_color"] != new_state["risk_color"]:
        return True
    return False


def should_recheck_l4(state: dict) -> bool:
    if not state.get("l4_active"):
        return False
    last = state.get("l4_last_check")
    if not last:
        return True
    last_time = datetime.fromisoformat(last.replace("Z", ""))
    return datetime.utcnow() - last_time >= timedelta(minutes=L4_RECHECK_MINUTES)
