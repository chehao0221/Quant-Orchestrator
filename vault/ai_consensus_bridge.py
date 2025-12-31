# ai_consensus_bridge.py
# 多 AI 共識橋樑（封頂最終版）
# 職責：
# - 聚合多個 AI 的意見
# - 標準化 score / veto / reason
# - 不做市場判斷、不寫 Vault、不發 Discord

from typing import Dict, Any, List, Optional
from shared.guardian_state import get_guardian_level


def build_consensus(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    messages 結構（每一筆）：
    {
        "ai": "AI_NAME",
        "payload": {
            "score": float,        # -1.0 ~ +1.0（可選）
            "penalty": float,      # -1.0 ~ 0.0（可選）
            "veto": bool,          # 是否否決（可選）
            "reason": str          # 說明（可選）
        }
    }
    """

    confidence = 0.5
    veto = False
    reasons: List[str] = []
    participants: List[str] = []

    for msg in messages:
        ai = msg.get("ai", "UNKNOWN_AI")
        payload = msg.get("payload", {})

        participants.append(ai)

        if payload.get("veto") is True:
            veto = True
            reasons.append(f"{ai}:VETO({payload.get('reason', 'no_reason')})")

        if isinstance(payload.get("score"), (int, float)):
            confidence += float(payload["score"])

        if isinstance(payload.get("penalty"), (int, float)):
            confidence += float(payload["penalty"])

        if isinstance(payload.get("reason"), str):
            reasons.append(f"{ai}:{payload['reason']}")

    # Guardian 狀態（僅讀）
    guardian_level: Optional[int] = get_guardian_level()

    # 信心值安全夾制
    confidence = max(0.0, min(1.0, confidence))

    return {
        "confidence": round(confidence, 4),
        "veto": veto,
        "guardian_level": guardian_level,
        "reasons": reasons,
        "participants": participants,
    }
