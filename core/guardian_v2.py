# core/guardian_v2.py
import time
from typing import Dict, Literal

from core.vault_access_guard import VaultAccessGuard, VaultAccessError


Market = Literal["TW", "US", "JP", "CRYPTO"]
Decision = Literal["PASS", "FREEZE", "REJECT"]


class GuardianError(Exception):
    pass


class GuardianV2:
    """
    Guardian V2（終極裁決者）
    ------------------------
    - 吃 evaluation_engine 的輸出
    - 套用硬規則 + 軟規則
    - 輸出 PASS / FREEZE / REJECT
    - 唯一合法寫入 LOCKED_DECISION/guardian
    """

    # ====== 門檻（一次定案，不追逐市場） ======
    HARD_SCORE_MIN = 0.25     # 任一市場低於此 → REJECT
    FREEZE_SCORE = 0.45       # 低於此 → 累計 freeze
    PASS_SCORE = 0.60         # 平均 ≥ 此 → PASS
    FREEZE_DAYS = 3           # 連續幾天低於 FREEZE_SCORE → FREEZE

    def __init__(self, vault_root: str):
        self.vault_root = vault_root
        self.guard = VaultAccessGuard(vault_root)

    # ---------- public API ----------

    def judge(
        self,
        date_yyyy_mm_dd: str,
        evaluation: Dict[Market, Dict],
        snapshot_complete: bool,
        history: Dict = None,
    ) -> Dict:
        """
        回傳裁決結果 dict，並寫入 LOCKED_DECISION
        """
        if not snapshot_complete:
            return self._finalize(
                decision="REJECT",
                date=date_yyyy_mm_dd,
                reason="snapshot incomplete",
                evaluation=evaluation,
                extra={"snapshot_complete": False},
            )

        if not evaluation:
            return self._finalize(
                decision="REJECT",
                date=date_yyyy_mm_dd,
                reason="no evaluation data",
                evaluation=evaluation,
            )

        # ---- 第一層：硬規則 ----
        for market, info in evaluation.items():
            score = info.get("score", 0.0)
            if score < self.HARD_SCORE_MIN:
                return self._finalize(
                    decision="REJECT",
                    date=date_yyyy_mm_dd,
                    reason=f"{market} score below HARD_SCORE_MIN",
                    evaluation=evaluation,
                    extra={"market": market, "score": score},
                )

        # ---- 第二層：軟規則 ----
        avg_score = sum(v["score"] for v in evaluation.values()) / len(evaluation)

        if avg_score >= self.PASS_SCORE:
            decision: Decision = "PASS"
        else:
            decision = "FREEZE"

        # ---- 連續 FREEZE 檢查（防慢性走壞） ----
        freeze_count = 0
        if history:
            freeze_count = int(history.get("consecutive_freeze", 0))

        if decision == "FREEZE" and avg_score < self.FREEZE_SCORE:
            freeze_count += 1
        else:
            freeze_count = 0

        if freeze_count >= self.FREEZE_DAYS:
            decision = "FREEZE"

        return self._finalize(
            decision=decision,
            date=date_yyyy_mm_dd,
            reason="guardian rule evaluation",
            evaluation=evaluation,
            extra={
                "avg_score": round(avg_score, 6),
                "consecutive_freeze": freeze_count,
            },
        )

    # ---------- internal ----------

    def _finalize(
        self,
        decision: Decision,
        date: str,
        reason: str,
        evaluation: Dict,
        extra: Dict = None,
    ) -> Dict:
        record = {
            "date": date,
            "decision": decision,
            "reason": reason,
            "evaluation": evaluation,
            "extra": extra or {},
            "timestamp": int(tim
