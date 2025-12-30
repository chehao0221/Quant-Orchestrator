# 系統人格守門 AI：防止風格漂移

def guard(persona_state: dict, current_decision: dict):
    drift = abs(
        persona_state.get("avg_confidence", 0.5)
        - current_decision.get("confidence", 0.5)
    )

    if drift > 0.3:
        return {
            "penalty": -0.25,
            "reason": "persona_drift_detected"
        }

    return {
        "penalty": 0.0,
        "reason": "persona_stable"
    }
