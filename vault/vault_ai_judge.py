def judge_final_confidence(bus_messages: dict):
    confidence = 0.5
    reasons = []

    for src, msg in bus_messages.items():
        if "score" in msg:
            confidence += msg["score"]
        if "penalty" in msg:
            confidence += msg["penalty"]
        reasons.append(f"{src}:{msg.get('reason')}")

    confidence = max(min(confidence, 1.0), 0.0)
    return confidence, reasons
