# vault_ai_judge.py
# 最終決策整合 AI（封頂版）
# 職責：
# - 彙整多 AI 訊息
# - 進行「互相約制」而非投票
# - 不產生原始市場判斷
# - 不寫 Vault、不學習、不發訊息
# - 輸出結果只供 Orchestrator 使用

from typing import Dict, List


# -------------------------------
# 公開 API
# -------------------------------

def judge(bridge_messages: List[Dict]) -> Dict:
    """
    bridge_messages: List[{
        "ai": str,
        "payload": {
            "score": float,      # 正向貢獻（-1 ~ +1）
            "penalty": float,    # 懲罰（負值）
            "veto": bool,        # 是否否決
            "reason": str        # 解釋（可選）
        }
    }]
    """

    # 初始中性信心
    confidence = 0.5
    veto = False
    reasons: List[str] = []

    # 約制用統計
    contributor_count = 0
    veto_sources = []

    for m in bridge_messages:
        ai_name = m.get("ai", "UNKNOWN_AI")
        payload = m.get("payload", {})

        # veto 永遠優先
        if payload.get("veto") is True:
            veto = True
            veto_sources.append(ai_name)
            if payload.get("reason"):
                reasons.append(f"{ai_name}:VETO({payload['reason']})")
            else:
                reasons.append(f"{ai_name}:VETO")

        # score / penalty 為可選
        if "score" in payload:
            try:
                confidence += float(payload["score"])
                contributor_count += 1
            except Exception:
                pass

        if "penalty" in payload:
            try:
                confidence += float(payload["penalty"])
                contributor_count += 1
            except Exception:
                pass

        if payload.get("reason") and not payload.get("veto"):
            reasons.append(f"{ai_name}:{payload['reason']}")

    # -------------------------------
    # 信心校準（互相約制核心）
    # -------------------------------

    # 多 AI 疊加時，進行貢獻稀釋，防止信心膨脹
    if contributor_count > 1:
        confidence = 0.5 + (confidence - 0.5) / contributor_count

    # 強制邊界
    confidence = round(max(min(confidence, 1.0), 0.0), 4)

    return {
        "confidence": confidence,
        "veto": veto,
        "veto_sources": veto_sources,
        "reasons": reasons
    }
