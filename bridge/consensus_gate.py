# consensus_gate.py
# 三方共識閘門（封頂最終版）
# 職責：
# - 彙整 Guardian / Stock-Genius / Orchestrator 意見
# - 判斷是否達成可執行共識
# - 決定 APPLY / BLOCK / SHRINK / ROLLBACK
# ❌ 不寫權重 ❌ 不學習 ❌ 不做市場分析

from typing import Dict, Any, Tuple

# =================================================
# 共識門檻鐵律
# =================================================

REQUIRE_GUARDIAN_APPROVAL = True
MIN_APPROVAL_SCORE = 2        # 三方至少 2 票同意
SHRINK_ON_DISAGREE = True    # 分歧時允許降權而非直接封鎖


# =================================================
# 公開 API
# =================================================

def resolve_consensus(
    guardian: Dict[str, Any],
    stock_genius: Dict[str, Any],
    orchestrator: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """
    每方輸入格式範例：
    {
        "approve": bool,
        "confidence": float,
        "reason": str
    }
    """

    votes = [
        ("guardian", guardian),
        ("stock_genius", stock_genius),
        ("orchestrator", orchestrator),
    ]

    approvals = sum(1 for _, v in votes if v.get("approve") is True)

    # Guardian 一票否決
    if REQUIRE_GUARDIAN_APPROVAL and not guardian.get("approve", False):
        return "BLOCK", {
            "reason": "GUARDIAN_VETO",
            "approvals": approvals
        }

    # 多數通過
    if approvals >= MIN_APPROVAL_SCORE:
        return "APPLY", {
            "approvals": approvals
        }

    # 分歧狀態
    if SHRINK_ON_DISAGREE:
        return "SHRINK", {
            "approvals": approvals,
            "reason": "CONSENSUS_WEAK"
        }

    return "BLOCK", {
        "approvals": approvals,
        "reason": "INSUFFICIENT_CONSENSUS"
    }
