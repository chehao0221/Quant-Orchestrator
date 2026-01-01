# core/guardian_v2.py
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Literal, Optional

from core.vault_access_guard import VaultAccessGuard

Decision = Literal["PASS", "REJECT", "FREEZE"]


@dataclass(frozen=True)
class GuardianThresholds:
    # 硬規則（任何一條不過 → REJECT / FREEZE）
    hard_score_min: float = 0.20          # 單一市場最低分
    hard_drawdown_min: float = -0.20      # 回撤底線（低於此視為嚴重）
    hard_fail_streak_max: int = 5         # 連敗上限（由 evaluation 提供/或缺省）

    # 軟規則（用於 PASS / FREEZE）
    pass_score: float = 0.60              # 平均分 ≥ pass_score 才 PASS
    freeze_score: float = 0.45            # 平均分介於 freeze_score~pass_score → FREEZE


class GuardianV2:
    """
    Guardian V2（終極封頂版）
    -------------------------
    - 只讀評估結果 / 投票 / 候選權重
    - 做出 PASS / REJECT / FREEZE
    - 並把 guardian_state.json 寫入 Quant-Vault/LOCKED_DECISION（透過 VaultAccessGuard）
    """

    def __init__(self, vault_root: str, thresholds: Optional[GuardianThresholds] = None):
        self.vault_root = Path(vault_root)
        self.thresholds = thresholds or GuardianThresholds()
        self.guard = VaultAccessGuard(str(self.vault_root))

        self.guardian_state_path = "LOCKED_DECISION/guardian/guardian_state.json"

    def evaluate(
        self,
        date_yyyy_mm_dd: str,
        evaluation: Dict,
        council_votes: Dict,
        proposed_weights: Dict,
        extra: Optional[Dict] = None,
    ) -> Dict:
        """
        evaluation 期望格式（由 evaluation_engine 提供）：
        {
          "TW": {"score": 0.62, "drawdown": -0.05, "fail_streak": 0, ...},
          "US": {...},
          ...
        }
        """

        # ---- 基本防呆 ----
        if not isinstance(evaluation, dict) or not evaluation:
            return self._finalize(
                decision="REJECT",
                date=date_yyyy_mm_dd,
                reason="evaluation_missing_or_invalid",
                evaluation=evaluation or {},
                extra={"council_votes": council_votes, "proposed_weights": proposed_weights, **(extra or {})},
            )

        # ---- 第一層：硬規則（任一市場觸發 → REJECT/FREEZE）----
        for market, info in evaluation.items():
            score = float(info.get("score", 0.0))
            dd = float(info.get("drawdown", 0.0))
            fail_streak = int(info.get("fail_streak", 0))

            if score < self.thresholds.hard_score_min:
                return self._finalize(
                    decision="REJECT",
                    date=date_yyyy_mm_dd,
                    reason=f"{market}_score_below_hard_min",
                    evaluation=evaluation,
                    extra={"market": market, "score": score, "threshold": self.thresholds.hard_score_min,
                           "council_votes": council_votes, "proposed_weights": proposed_weights, **(extra or {})},
                )

            # 回撤太嚴重 → FREEZE（不一定 REJECT，讓系統冷靜）
            if dd < self.thresholds.hard_drawdown_min:
                return self._finalize(
                    decision="FREEZE",
                    date=date_yyyy_mm_dd,
                    reason=f"{market}_drawdown_below_hard_min",
                    evaluation=evaluation,
                    extra={"market": market, "drawdown": dd, "threshold": self.thresholds.hard_drawdown_min,
                           "council_votes": council_votes, "proposed_weights": proposed_weights, **(extra or {})},
                )

            if fail_streak >= self.thresholds.hard_fail_streak_max:
                return self._finalize(
                    decision="FREEZE",
                    date=date_yyyy_mm_dd,
                    reason=f"{market}_fail_streak_too_high",
                    evaluation=evaluation,
                    extra={"market": market, "fail_streak": fail_streak, "threshold": self.thresholds.hard_fail_streak_max,
                           "council_votes": council_votes, "proposed_weights": proposed_weights, **(extra or {})},
                )

        # ---- 第二層：軟規則（看平均分，決定 PASS / FREEZE / REJECT）----
        scores = []
        for info in evaluation.values():
            try:
                scores.append(float(info.get("score", 0.0)))
            except Exception:
                scores.append(0.0)

        avg_score = sum(scores) / max(len(scores), 1)

        if avg_score >= self.thresholds.pass_score:
            decision: Decision = "PASS"
            reason = "avg_score_pass"
        elif avg_score >= self.thresholds.freeze_score:
            decision = "FREEZE"
            reason = "avg_score_freeze"
        else:
            decision = "REJECT"
            reason = "avg_score_reject"

        return self._finalize(
            decision=decision,
            date=date_yyyy_mm_dd,
            reason=reason,
            evaluation=evaluation,
            extra={"avg_score": avg_score, "thresholds": self.thresholds.__dict__,
                   "council_votes": council_votes, "proposed_weights": proposed_weights, **(extra or {})},
        )

    def _finalize(
        self,
        decision: Decision,
        date: str,
        reason: str,
        evaluation: Dict,
        extra: Dict,
    ) -> Dict:
        """
        統一輸出 + 寫入 Quant-Vault/LOCKED_DECISION/guardian/guardian_state.json
        """
        record = {
            "date": date,
            "decision": decision,
            "reason": reason,
            "evaluation": evaluation,
            "extra": extra or {},
            "timestamp": int(datetime.utcnow().timestamp()),
        }

        # guardian_state（治理狀態）— 必須走 VaultAccessGuard
        state_payload = {
            "date": date,
            "state": decision,
            "freeze": (decision == "FREEZE"),
            "reason": reason,
            "timestamp": record["timestamp"],
        }

        self.guard.write_json(
            role="guardian",
            relative_path=self.guardian_state_path,
            payload=state_payload,
            reason=f"guardian_v2:{reason}",
        )

        return record
