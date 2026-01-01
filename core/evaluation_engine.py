# core/evaluation_engine.py
import json
from pathlib import Path
from typing import Dict, Literal, Tuple


Market = Literal["TW", "US", "JP", "CRYPTO"]


class EvaluationError(Exception):
    pass


class EvaluationEngine:
    """
    客觀績效評估引擎（只讀）
    讀取：TEMP_CACHE/snapshot/YYYY-MM-DD/<MARKET>.json
    輸出：
      - eval_scores: {market: score(0~1)}
      - eval_evidence: {market: {score, components, metrics}}
    """

    WEIGHTS = {
        "return": 0.30,
        "drawdown": 0.30,
        "volatility": 0.15,
        "win_rate": 0.15,
        "confidence": 0.10,
    }

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()

    def run(self, date_key: str) -> Tuple[Dict[Market, float], Dict]:
        results = self.evaluate_day(date_key)
        scores = {m: float(results[m]["score"]) for m in results}
        return scores, results

    def evaluate_day(self, date_key: str) -> Dict[Market, Dict]:
        base = self.vault_root / "TEMP_CACHE" / "snapshot" / date_key
        markets = ["TW", "US", "JP", "CRYPTO"]

        out: Dict[Market, Dict] = {}
        for m in markets:
            p = base / f"{m}.json"
            if not p.exists():
                # 缺報告：直接給 0 分（保守）
                out[m] = {
                    "score": 0.0,
                    "components": {},
                    "metrics": {},
                    "reason": f"missing_report:{p}",
                }
                continue

            report = self._load_report(p)
            metrics = report.get("metrics", {})
            comps = self._score_components(metrics)
            total = self._aggregate_score(comps)

            out[m] = {
                "score": round(total, 6),
                "components": {k: round(v, 6) for k, v in comps.items()},
                "metrics": metrics,
            }

        return out

    @staticmethod
    def _load_report(path: Path) -> dict:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return raw["data"] if "data" in raw else raw
        except Exception as e:
            raise EvaluationError(f"無法讀取報告檔案: {path} ({e})")

    def _score_components(self, metrics: dict) -> Dict[str, float]:
        r = float(metrics.get("return", 0.0))
        dd = float(metrics.get("drawdown", 1.0))
        vol = float(metrics.get("volatility", 1.0))
        wr = float(metrics.get("win_rate", 0.0))
        conf = float(metrics.get("confidence", 0.0))

        return {
            "return": self._score_return(r),
            "drawdown": self._score_drawdown(dd),
            "volatility": self._score_volatility(vol),
            "win_rate": self._clamp01(wr),
            "confidence": self._clamp01(conf),
        }

    def _aggregate_score(self, comps: Dict[str, float]) -> float:
        score = 0.0
        for k, w in self.WEIGHTS.items():
            score += comps.get(k, 0.0) * w
        return self._clamp01(score)

    @staticmethod
    def _score_return(r: float) -> float:
        # -5% => 0, +5% => 1（保守線性）
        lo, hi = -0.05, 0.05
        if r <= lo:
            return 0.0
        if r >= hi:
            return 1.0
        return (r - lo) / (hi - lo)

    @staticmethod
    def _score_drawdown(dd: float) -> float:
        # 0% => 1, 30% => 0
        if dd <= 0:
            return 1.0
        if dd >= 0.30:
            return 0.0
        return 1.0 - (dd / 0.30)

    @staticmethod
    def _score_volatility(vol: float) -> float:
        # 0 => 1, 5% => 0
        if vol <= 0:
            return 1.0
        if vol >= 0.05:
            return 0.0
        return 1.0 - (vol / 0.05)

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))
