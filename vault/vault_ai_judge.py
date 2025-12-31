# Quant-Orchestrator/vault/vault_ai_judge.py
# 最終決策整合 AI（封頂最終版｜可直接完整覆蓋）
# 職責：
# - 接收多 AI 共識橋樑輸出
# - 做最終一致性裁決（confidence / veto）
# - 不產生原始市場判斷
# - 不寫 Vault
#
# ✅ 與 ai_consensus_bridge 完整對接
# ✅ 支援多 AI、veto、信心加權
# ✅ 作為 Orchestrator → 發文 / 學習 的唯一裁決層

from typing import Dict, Any, List


def judge(consensus: Dict[str, Any]) -> Dict[str, Any]:
    """
    consensus 來源：ai_consensus_bridge.build_consensus()

    預期結構：
    {
        "confidence": float,
        "veto": bool,
        "guardian_level": Optional[int],
        "reasons": List[str],
        "participants": List[str]
    }
    """

    confidence = float(consensus.get("confidence", 0.5))
    veto = bool(consensus.get("veto", False))
    guardian_level = consensus.get("guardian_level")
    reasons: List[str] = consensus.get("reasons", [])
    participants: List[str] = consensus.get("participants", [])

    # 絕對安全夾制（雙保險）
    confidence = max(0.0, min(1.0, confidence))

    return {
        "final_confidence": round(confidence, 4),
        "veto": veto,
        "guardian_level": guardian_level,
        "reasons": reasons,
        "participants": participants,
        "status": "BLOCKED" if veto else "APPROVED"
    }
