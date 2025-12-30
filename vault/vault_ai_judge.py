# 最終決策整合 AI（不產生原始判斷）

def judge(bridge_messages: list):
    confidence = 0.5
    veto = False
    reasons = []

    for m in bridge_messages:
        p = m["payload"]

        if p.get("veto"):
            veto = True
            reasons.append(f'{m["ai"]}:VETO({p.get("reason")})')

        if "score" in p:
            confidence += p["score"]

        if "penalty" in p:
            confidence += p["penalty"]

        if "reason" in p:
            reasons.append(f'{m["ai"]}:{p["reason"]}')

    confidence = max(min(confidence, 1.0), 0.0)

    return {
        "confidence": confidence,
        "veto": veto,
        "reasons": reasons
    }
