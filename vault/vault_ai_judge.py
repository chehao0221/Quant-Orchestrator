# 最終決策整合 AI（不產生原始判斷）
# 職責：整合、制衡、封頂，不給市場方向

from typing import List, Dict


MAX_CONFIDENCE = 1.0
MIN_CONFIDENCE = 0.0

MAX_SINGLE_AI_SCORE = 0.2     # 單一 AI 最大影響力
MAX_TOTAL_SCORE = 0.5         # 全體 AI 最大疊加幅度


def judge(bridge_messages: List[Dict]) -> Dict:
    confidence = 0.5
    veto = False
    reasons = []

    total_delta = 0.0

    for m in bridge_messages:
        payload = m.get("payload", {})
        ai_name = m.get("ai", "UNKNOWN")

        # 1️⃣ VETO 絕對優先
        if payload.get("veto"):
            veto = True
            reasons.append(f"{ai_name}:VETO({payload.get('reason')})")
            continue

        delta = 0.0

        # 2️⃣ Score（單 AI 封頂）
        if isinstance(payload.get("score"), (int, float)):
            delta += max(
                -MAX_SINGLE_AI_SCORE,
                min(MAX_SINGLE_AI_SCORE, payload["score"])
            )

        # 3️⃣ Penalty（必須為負值，否則忽略）
        if isinstance(payload.get("penalty"), (int, float)) and payload["penalty"] < 0:
            delta += payload["penalty"]

        # 4️⃣ 累計全體影響（總封頂）
        total_delta += delta
        total_delta = max(-MAX_TOTAL_SCORE, min(MAX_TOTAL_SCORE, total_delta))

        if payload.get("reason"):
            reasons.append(f"{ai_name}:{payload['reason']}")

    confidence += total_delta
    confidence = max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence))

    return {
        "confidence": confidence,
        "veto": veto,
        "reasons": reasons
    }
