# vault/vault_ai_judge.py
# 最終決策整合 AI（封頂 120 分版）
# ✅ 不產生原始判斷
# ✅ 不改輸出結構
# ✅ 多 AI 共識、互相約制、過熱自抑
# ✅ 無資料＝不給結論（防誤判）
# ✅ 可長期自我穩定

from typing import List, Dict

# === 共識治理參數（鐵律層）===
BASE_CONFIDENCE = 0.5
MIN_AI_COUNT = 2                 # 至少 2 個 AI 才允許形成結論
MAX_SINGLE_IMPACT = 0.15         # 單一 AI 對信心值最大影響
OVERHEAT_THRESHOLD = 0.75        # 群體信心過熱門檻
OVERHEAT_PENALTY = -0.10         # 過熱自抑懲罰
CONSENSUS_SPREAD_LIMIT = 0.35    # AI 意見分歧過大時降權


def judge(bridge_messages: List[Dict]) -> Dict:
    """
    多 AI 最終共識判斷器（只整合，不生成）
    """

    # ---------- 空資料防護 ----------
    if not bridge_messages or len(bridge_messages) < MIN_AI_COUNT:
        return {
            "confidence": 0.0,
            "veto": False,
            "reasons": ["SYSTEM:NO_DATA_OR_INSUFFICIENT_AI"]
        }

    confidence = BASE_CONFIDENCE
    veto = False
    reasons = []

    scores = []

    # ---------- 個別 AI 處理 ----------
    for m in bridge_messages:
        ai_name = m.get("ai", "UNKNOWN_AI")
        payload = m.get("payload", {})

        # 防止 payload 異常
        if not isinstance(payload, dict):
            reasons.append(f"{ai_name}:INVALID_PAYLOAD")
            continue

        # veto 永遠最高優先
        if payload.get("veto"):
            veto = True
            reasons.append(f"{ai_name}:VETO({payload.get('reason')})")
            continue

        delta = 0.0

        if "score" in payload and isinstance(payload["score"], (int, float)):
            delta += payload["score"]

        if "penalty" in payload and isinstance(payload["penalty"], (int, float)):
            delta += payload["penalty"]

        # 單一 AI 影響封頂（防極端）
        if delta > MAX_SINGLE_IMPACT:
            delta = MAX_SINGLE_IMPACT
        elif delta < -MAX_SINGLE_IMPACT:
            delta = -MAX_SINGLE_IMPACT

        confidence += delta
        scores.append(delta)

        if "reason" in payload:
            reasons.append(f"{ai_name}:{payload['reason']}")

    # ---------- 群體分歧檢查 ----------
    if scores:
        spread = max(scores) - min(scores)
        if spread > CONSENSUS_SPREAD_LIMIT:
            confidence -= abs(spread) * 0.1
            reasons.append("SYSTEM:CONSENSUS_SPREAD_HIGH")

    # ---------- 群體過熱自抑 ----------
    if confidence > OVERHEAT_THRESHOLD:
        confidence += OVERHEAT_PENALTY
        reasons.append("SYSTEM:OVERHEAT_SELF_REGULATION")

    # ---------- 最終封頂 ----------
    confidence = max(min(confidence, 1.0), 0.0)

    return {
        "confidence": confidence,
        "veto": veto,
        "reasons": reasons
    }
