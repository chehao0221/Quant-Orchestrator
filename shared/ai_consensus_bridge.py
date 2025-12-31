# Quant-Orchestrator/shared/ai_consensus_bridge.py
# 多 AI 共識橋樑（封頂最終版｜可直接完整覆蓋）
# 職責：
# - 彙整 Quant-Guardian-Ultra / Stock-Genius-System / Orchestrator 子 AI 的輸出
# - 不判斷市場、不學習、不寫 Vault
# - 只做「結構化共識整合」
#
# ✅ 支援多 AI
# ✅ 支援 veto / score / penalty
# ✅ 作為 vault_ai_judge 的唯一上游

from typing import List, Dict, Any


def build_consensus(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    messages 結構範例：
    [
        {
            "ai": "Stock-Genius-TW",
            "payload": {
                "score": 0.12,
                "confidence": 0.68,
                "reason": "MACD + RSI 共振"
            }
        },
        {
            "ai": "Guardian-Ultra",
            "payload": {
                "veto": True,
                "level": 4,
                "reason": "黑天鵝風險升高"
            }
        }
    ]
    """

    confidence = 0.5
    veto = False
    guardian_level = None
    reasons: List[str] = []
    participants: List[str] = []

    for m in messages:
        ai_name = m.get("ai", "UNKNOWN")
        payload = m.get("payload", {})

        participants.append(ai_name)

        # Guardian veto（最高優先）
        if payload.get("veto") is True:
            veto = True
            guardian_level = payload.get("level")
            reasons.append(f"{ai_name}:VETO({payload.get('reason')})")
            continue

        # 正向 / 反向貢獻
        if "score" in payload:
            confidence += float(payload["score"])

        if "penalty" in payload:
            confidence += float(payload["penalty"])

        # 理由彙整
        if "reason" in payload:
            reasons.append(f"{ai_name}:{payload['reason']}")

    # 防止爆衝
    confidence = max(0.0, min(1.0, confidence))

    return {
        "confidence": round(confidence, 4),
        "veto": veto,
        "guardian_level": guardian_level,
        "reasons": reasons,
        "participants": participants,
    }
