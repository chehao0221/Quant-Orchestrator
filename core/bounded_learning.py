# core/bounded_learning.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Literal, Tuple


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class LearningConfig:
    step_max: float = 0.05        # 單次權重變動 ≤ 5%
    cap_max: float = 0.40         # 單一市場權重上限 ≤ 40%
    cooldown_days: int = 21       # 學習冷卻 ≥ 21 天
    min_weight: float = 0.05      # 最低保留（避免被歸零）
    normalize_eps: float = 1e-12


class BoundedLearning:
    """
    有上限學習（封頂保守）
    輸入：current_weights, eval_scores, council_votes, guardian_state, learning_state
    輸出：proposed_weights, new_learning_state, reason, evidence
    """

    def __init__(self, cfg: LearningConfig | None = None):
        self.cfg = cfg or LearningConfig()

    def propose(
        self,
        date_key: str,
        current_weights: Dict[Market, float],
        eval_scores: Dict[Market, float],
        council_votes: Dict[Market, float],
        guardian_state: Dict,
        learning_state: Dict,
    ) -> Tuple[Dict[Market, float], Dict, str, Dict]:

        markets = ["TW", "US", "JP", "CRYPTO"]
        cur = {m: float(current_weights.get(m, 0.25)) for m in markets}
        cur = self._normalize(cur)

        # 冷卻判定
        last = (learning_state or {}).get("last_update")
        if last:
            try:
                last_dt = datetime.strptime(last, "%Y-%m-%d")
                if datetime.strptime(date_key, "%Y-%m-%d") < last_dt + timedelta(days=self.cfg.cooldown_days):
                    return cur, (learning_state or {}), "cooldown_skip", {"cooldown": True, "last_update": last}
            except Exception:
                pass

        freeze = (guardian_state or {}).get("freeze", {}) if isinstance(guardian_state, dict) else {}

        # 產生偏好方向：eval + council
        raw_delta = {}
        for m in markets:
            score = float(eval_scores.get(m, 0.0))
            vote = float(council_votes.get(m, 0.0))
            # score 中性化（0.5為中點），加上 vote
            raw_delta[m] = (score - 0.5) * 0.06 + vote * 0.04  # 很保守

            # freeze 直接朝下
            if bool(freeze.get(m, False)):
                raw_delta[m] -= 0.05

        # 套單次變動上限
        proposed = {}
        for m in markets:
            d = self._clamp(raw_delta[m], -self.cfg.step_max, self.cfg.step_max)
            proposed[m] = cur[m] + d

        # 套上下限
        for m in markets:
            proposed[m] = self._clamp(proposed[m], self.cfg.min_weight, self.cfg.cap_max)

        proposed = self._normalize(proposed)

        new_state = dict(learning_state or {})
        new_state["last_update"] = date_key
        new_state["cooldown_days"] = self.cfg.cooldown_days

        evidence = {
            "current": cur,
            "delta_raw": raw_delta,
            "council_votes": council_votes,
            "eval_scores": eval_scores,
            "freeze": freeze,
            "config": self.cfg.__dict__,
        }
        return proposed, new_state, "bounded_update", evidence

    def _normalize(self, w: Dict[Market, float]) -> Dict[Market, float]:
        s = sum(float(v) for v in w.values())
        if s <= self.cfg.normalize_eps:
            return {m: 0.25 for m in w}
        return {m: float(v) / s for m, v in w.items()}

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(x)))
