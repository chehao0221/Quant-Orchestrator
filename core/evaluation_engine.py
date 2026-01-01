# core/evaluation_engine.py
import json
from pathlib import Path
from typing import Dict, Literal


Market = Literal["TW", "US", "JP", "CRYPTO"]


class EvaluationError(Exception):
    pass


class EvaluationEngine:
    """
    客觀績效評估引擎（只讀）
    ------------------------
    - 只讀 TEMP_CACHE/snapshot
    - 不寫任何 Vault
    - 不接受策略輸入
    - 輸出可解釋的分數
    """

    MARKET_FILES: Dict[Market, str] = {
        "TW": "tw.json",
        "US": "us.json",
        "JP": "jp.json",
        "CRYPTO": "crypto.json",
    }

    # 評分權重（總和 = 1.0）
    WEIGHTS = {
        "return": 0.30,
        "drawdown": 0.30,
        "volatility": 0.20,
        "win_rate": 0.10,
        "confidence": 0.10,
    }

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.snapshot_root = (self.vault_root / "TEMP_CACHE" / "snapshot").resolve()

        if not self.snapshot_root.exists():
            raise EvaluationError(f"snapshot 目錄不存在: {self.snapshot_root}")

    # ---------- public API ----------

    def evaluate_day(self, date_yyyy_mm_dd: str) -> Dict[Market, Dict]:
        """
        評估指定日期所有市場
        回傳：
          { market: { score, components } }
        """
        day_dir = (self.snapshot_root / date_yyyy_mm_dd).resolve()
        if not day_dir.exists():
            raise EvaluationError(f"找不到 snapshot 日期資料: {date_yyyy_mm_dd}")

        results: Dict[Market, Dict] = {}

        for market, fname in self.MARKET_FILES.items():
            path = day_dir / fname
            if not path.exists():
                # 缺市場資料 → 不評分（由 Guardian 決定怎麼處理）
                continue

            report = self._load_report(path)
            components = self._score_components(report["metrics"])
            total_score = self._aggregate_score(components)

            results[market] = {
                "score": round(total_score, 6),
                "components": {k: round(v, 6) for k, v in components.items()}
            }

        return results

    # ---------- internal ----------

    @staticmethod
    def _load_report(path: Path) -> dict:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return raw["data"] if "data" in raw else raw
        except Exception as e:
            raise EvaluationError(f"無法讀取報告檔案: {path} ({e})")

    def _score_components(self, metrics: dict) -> Dict[str, float]:
        """
        將原始 metrics 正規化成 0~1 分數
        """
        r = float(metrics["return"])
        dd = float(metrics["drawdown"])
        vol = float(metrics["volatility"])
        wr = float(metrics["win_rate"])
        conf = float(metrics["confidence"])

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
            score += comps[k] * w
        return self._clamp01(score)

    # ---------- scoring rules ----------

    @staticmethod
    def _score_return(r: float) -> float:
        """
        報酬不是線性獎勵，避免短期爆衝
        """
        if r <= 0:
            return 0.0
        if r >= 0.05:
            return 1.0
        return r / 0.05

    @staticmethod
    def _score_drawdown(dd: float) -> float:
        """
        回撤越小越好
        dd 通常是負值
        """
        if dd >= 0:
            return 1.0
        if dd <= -0.10:
            return 0.0
        return 1.0 + (dd / 0.10)

    @staticmethod
    def _score_volatility(vol: float) -> float:
        """
        波動越低越好
        """
        if vol <= 0:
            return 1.0
        if vol >= 0.05:
            return 0.0
        return 1.0 - (vol / 0.05)

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))
