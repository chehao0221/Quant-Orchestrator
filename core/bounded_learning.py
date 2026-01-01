# core/bounded_learning.py
import json
import time
from dataclasses import dataclass
from typing import Dict, Literal, Tuple


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class LearningCaps:
    max_step_abs: float = 0.05     # 單次權重變動 ≤ 5%
    max_weight: float = 0.40       # 單策略最大權重 ≤ 40%
    min_weight: float = 0.05       # 單策略最小權重 ≥ 5%（避免被歸零造成震盪）
    cooldown_days: int = 21        # 學習冷卻 ≥ 21 天


class BoundedLearning:
    """
    封頂學習：只輸出「新權重建議」，不直接寫入 Vault。
    寫入只能由 governance_writer 執行。
    """

    def __init__(self, caps: LearningCaps | None = None):
        self.caps = caps or LearningCaps()

    def propose_new_weights(
        self,
        current_weights: Dict[Market, float],
        eval_scores: Dict[Market, float],
        council_votes: Dict[Market, float],
        learning_state: Dict,
        guardian_result: Dict,
    ) -> Tuple[Dict[Market, float], Dict]:
        """
        回傳：
        - proposed_weights: 新權重（已正規化）
        - new_learning_state: 更新後 learning_state（含 last_learn_ts 等）
        """

        now = int(time.time())
        if not self._guardian_allows_learning(guardian_result):
            return current_weights, self._touch_state(learning_state, now, "guardian_block")

        if not self._cooldown_ok(learning_state, now):
            return current_weights, self._touch_state(learning_state, now, "cooldown_block")

        markets = ["TW", "US", "JP", "CRYPTO"]
        w = {m: float(current_weights.get(m, 0.0)) for m in markets}

        # 學習信號：eval_score（0~1）+ council_vote（-0.3~+0.3）
        # 形成 target drift：高分/正向投票 → 微增；低分/負向投票 → 微減
        # drift 控制在 [-max_step, +max_step]
        proposed = {}
        for m in markets:
            score = float(eval_scores.get(m, 0.0))
            vote = float(council_votes.get(m, 0.0))

            # 基於 score 的微調：score>0.5 增，<0.5 減，幅度最多 0.03
            score_drift = (score - 0.5) * 0.06  # [-0.03, +0.03]
            drift = score_drift + vote  # vote 本身已被 clamp

            drift = self._clamp(drift, -self.caps.max_step_abs, self.caps.max_step_abs)
            proposed[m] = w[m] * (1.0 + drift)

        # clamp each weight
        for m in markets:
            proposed[m] = self._clamp(proposed[m], self.caps.min_weight, self.caps.max_weight)

        # normalize to sum=1
        proposed = self._normalize(proposed, markets)

        new_state = dict(learning_state or {})
        new_state["last_learn_ts"] = now
        new_state["last_action"] = "learn_applied"
        new_state["cooldown_days"] = self.caps.cooldown_days

        return proposed, new_state

    @staticmethod
    def _guardian_allows_learning(guardian_result: Dict) -> bool:
        # 支援格式：
        # {"status": "PASS"} or {"decision": "PASS"}
        s = (guardian_result.get("status") or guardian_result.get("decision") or "").upper()
        return s == "PASS"

    def _cooldown_ok(self, learning_state: Dict, now: int) -> bool:
        last = int((learning_state or {}).get("last_learn_ts", 0))
        if last <= 0:
            return True
        return (now - last) >= self.caps.cooldown_days * 86400

    @staticmethod
    def _touch_state(state: Dict, now: int, reason: str) -> Dict:
        out = dict(state or {})
        out["last_check_ts"] = now
        out["last_action"] = reason
        return out

    @staticmethod
    def _normalize(w: Dict[str, float], markets) -> Dict[str, float]:
        s = sum(max(0.0, float(w[m])) for m in markets)
        if s <= 0:
            # fallback 平均
            return {m: 1.0 / len(markets) for m in markets}
        return {m: float(w[m]) / s for m in markets}

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, x))
