# 多 AI 共識橋樑（唯一決策入口）

def ai_consensus(analysis: dict, audit: dict, guardian_view: dict) -> dict:
    if not guardian_view["allow_stock"]:
        return {
            "final": False,
            "reason": "GUARDIAN_BLOCK"
        }

    score = analysis["score"] + guardian_view["risk_bias"]

    if score <= 0:
        return {
            "final": False,
            "reason": "RISK_OVERRIDE"
        }

    return {
        "final": True,
        "adjusted_score": max(score, 0)
    }
