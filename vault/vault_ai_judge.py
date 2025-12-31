# Quant-Orchestrator/vault/vault_ai_judge.py
# 最終決策整合 AI（封頂最終版｜可直接完整覆蓋）
# 職責：
# - 接收三方 AI 共識橋樑輸出
# - 做「最終風險收斂與一致性裁決」
# - 僅輸出結構化結果
#
# ❌ 不產生原始判斷
# ❌ 不寫 Vault
# ❌ 不發 Discord
# ❌ 不學習
#
# ✅ 作為 Orchestrator 的「最後一道一致性門」

from typing import Dict, Any, List


def judge(consensus: Dict[str, Any]) -> Dict[str, Any]:
    """
    consensus 來源：shared.ai_consensus_bridge.build_consensus()

    預期輸入結構：
    {
        "confidence": float,
        "veto": bool,
        "guardian_level": int | None,
        "signals": [str],
        "reasons": [str],
        "participants": [str]
    }
    """

    # -------------------------------
    # 基本防禦檢查（鐵律）
    # -------------------------------
    if not isinstance(consensus, dict):
        raise ValueError("Invalid consensus payload")

    confidence = float(consensus.get("confidence", 0.5))
    veto = bool(consensus.get("veto", False))
    guardian_level = consensus.get("guardian_level")
    reasons: List[str] = consensus.get("reasons", [])
    participants: List[str] = consensus.get("participants", [])

    # -------------------------------
    # Guardian 最終否決權（不可覆寫）
    # -------------------------------
    if veto:
        return {
            "allowed": False,
            "confidence": 0.0,
            "guardian_level": guardian_level,
            "reason": "GUARDIAN_VETO",
            "detail": reasons,
            "participants": participants,
        }

    # -------------------------------
    # 信心邊界收斂（防爆衝）
    # -------------------------------
    confidence = max(0.0, min(1.0, confidence))

    # -------------------------------
    # 最終一致性輸出
    # -------------------------------
    return {
        "allowed": True,
        "confidence": round(confidence, 4),
        "guardian_level": guardian_level,
        "reason": "CONSENSUS_OK",
        "detail": reasons,
        "participants": participants,
    }
