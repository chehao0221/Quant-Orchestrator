# 反對派 AI：只負責找「不該發」的理由

def evaluate(context: dict):
    penalties = []
    reasons = []

    if context.get("confidence", 0) > 0.7 and context.get("market_volatility", 0) > 0.6:
        penalties.append(-0.3)
        reasons.append("high_confidence_under_high_volatility")

    if context.get("ai_agreement_rate", 1.0) > 0.9:
        penalties.append(-0.2)
        reasons.append("over_consensus_risk")

    return {
        "penalty": sum(penalties),
        "reason": ";".join(reasons) or "no_objection"
    }
