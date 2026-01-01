# core/council_engine.py
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Literal


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class CouncilConfig:
    # 互評只影響「權限/上限」，不改策略邏輯
    # 互評分數範圍：[-0.3, +0.3]
    max_vote_abs: float = 0.30

    # 評估分數（0~1）越高越能加權
    # 互評實際輸出 = clamp(vote) * (0.5 + 0.5*eval_score)
    eval_influence_floor: float = 0.50  # 讓低分也有最小影響，但不會爆

    # 若某市場被 guardian freeze，可直接給負向，避免拖累整體
    freeze_penalty: float = -0.20


class CouncilEngine:
    """
    策略互評（只影響權限/上限，不改策略邏輯）
    輸入：evaluation 分數、guardian 狀態
    輸出：各市場 vote（-0.3~+0.3）
    """

    def __init__(self, config: CouncilConfig | None = None):
        self.cfg = config or CouncilConfig()

    def run(
        self,
        eval_scores: Dict[Market, float],
        guardian_state: Dict,
    ) -> Dict[Market, float]:
        freeze_map = self._freeze_map(guardian_state)

        # 最簡潔且穩健的互評規則：
        # - 以 eval_scores 高低排序：高者微加、低者微減（總和接近 0）
        # - 若 freeze：直接施加 freeze_penalty
        markets = ["TW", "US", "JP", "CRYPTO"]
        base = {m: 0.0 for m in markets}

        # freeze 先處理
        for m in markets:
            if freeze_map.get(m, False):
                base[m] += self.cfg.freeze_penalty

        # 依評估分數排序（忽略 freeze 的市場也照排序，但其 base 已懲罰）
        ranked = sorted(markets, key=lambda x: eval_scores.get(x, 0.0), reverse=True)

        # 分配小幅差異：最高 +0.10、次高 +0.05、次低 -0.05、最低 -0.10
        # JP 若你未啟用可保持 0；這裡仍保留通用性
        deltas = [0.10, 0.05, -0.05, -0.10]
        for m, d in zip(ranked, deltas):
            base[m] += d

        # 根據 eval score 調整影響力
        out: Dict[Market, float] = {}
        for m in markets:
            score = float(eval_scores.get(m, 0.0))
            influence = self.cfg.eval_influence_floor + (1.0 - self.cfg.eval_influence_floor) * score
            v = base[m] * influence
            out[m] = float(self._clamp(v, -self.cfg.max_vote_abs, self.cfg.max_vote_abs))

        return out

    @staticmethod
    def _freeze_map(guardian_state: Dict) -> Dict[Market, bool]:
        # 允許兩種格式：
        # 1) {"freeze": {"TW": false, ...}}
        # 2) {"TW": {"freeze": false}, ...}
        if "freeze" in guardian_state and isinstance(guardian_state["freeze"], dict):
            return guardian_state["freeze"]
        out = {}
        for k, v in guardian_state.items():
            if isinstance(v, dict) and "freeze" in v:
                out[k] = bool(v["freeze"])
        return out

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, x))
