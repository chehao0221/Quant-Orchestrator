# Guardian → AI 語意橋樑（不可直接做決策）

def interpret_guardian_state(state: dict) -> dict:
    level = state.get("level", "L0")

    if level in ["L4", "L5"]:
        return {
            "allow_stock": False,
            "risk_bias": -1.0,
            "mode": "BLACK_SWAN"
        }

    if level == "L3":
        return {
            "allow_stock": True,
            "risk_bias": -0.3,
            "mode": "DEFENSIVE"
        }

    return {
        "allow_stock": True,
        "risk_bias": 0.0,
        "mode": "NORMAL"
    }
