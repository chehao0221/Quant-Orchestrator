# core/council_engine.py
from dataclasses import dataclass
from typing import Dict, Literal


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class CouncilConfig:
    # 互評只影響「權限/上限」，不改策略邏輯
    # 投票範圍：[-0.30, +0.30]
    max_vote_abs: float = 0.30
    freeze_penalty: float = -0.20


class CouncilEngine:
    """
    最小、穩健、可解釋的互評：
    - 分數高者微加、低者微減（總和接近 0）
    - 被 guardian freeze 的市場：直接加上 freeze_penalty
    """

    def __init__(self, cfg: CouncilConfig | None = None):
        self.cfg = cfg or CouncilConfig()

    def run(self, eval_scores: Dict[Market, float], guardian_state: Dict) -> Dict[Market, float]:
        markets = ["TW", "US", "JP", "CRYPTO"]
        freeze_map = (guardian_state or {}).get("freeze", {}) if isinstance(guardian_state, dict) else {}

        # 依分數排序
        ranked = sorted(markets, key=lambda m: float(eval_scores.get(m, 0.0)), reverse=True)

        base = {m: 0.0 for m in markets}
        deltas = [0.10, 0.05, -0.05, -0.10]  # 固定、保守

        for m, d in zip(ranked, deltas):
            base[m] += d

        # freeze penalty
        for m in markets:
            if bool(freeze_map.get(m, False)):
                base[m] += self.cfg.freeze_penalty

        # clamp
        out = {m: self._clamp(base[m], -self.cfg.max_vote_abs, self.cfg.max_vote_abs) for m in markets}
        return out

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(x)))
