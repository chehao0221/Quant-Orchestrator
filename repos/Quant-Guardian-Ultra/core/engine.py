# core/engine.py
from risk_policy import resolve_risk
from notifier import notify_risk

def run_engine(state):
    """
    Guardian main engine
    """
    level = state.get("risk_level", 1)
    reason = state.get("reason", "N/A")

    policy = resolve_risk(level)

    # 通知（L3 / L4）
    notify_risk(level, reason)

    # L4+ → 直接停
    if policy["action"] == "STOP_AI":
        print("[Guardian] L4+ detected, all stock systems halted")
        return

    # L1–L3 才會跑到這裡
    run_stock_systems()

def run_stock_systems():
    """
    Placeholder: actual stock AI / explorer calls
    """
    print("[Guardian] Stock systems running (L1–L3)")
