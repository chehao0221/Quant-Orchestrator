# core/council_engine.py
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class CouncilEngine:
    """
    策略互評（Council）
    -------------------
    - 只讀 reports（標準化結果輸出）
    - 輸出「互評分數 / 建議調整」給 guardian 或 governance 參考
    - 絕不修改策略邏輯，絕不寫入 Vault

    互評原則（保守）：
    1) 高回撤 / 高波動 → 扣分
    2) 低勝率 / 低信心 → 扣分
    3) 穩定（低回撤 + 低波動 + 中高勝率）→ 加分
    """

    def __init__(
        self,
        snapshot_root: str,
        markets: Optional[List[str]] = None,
    ):
        self.snapshot_root = Path(snapshot_root)
        self.markets = markets or ["TW", "US", "JP", "CRYPTO"]

    # ---------------- public API ----------------

    def run_daily_review(self, date_str: str) -> Dict[str, Any]:
        """
        輸入 date_str: 'YYYY-MM-DD'
        讀取 TEMP_CACHE/snapshot/YYYY-MM-DD/* 報告
        回傳：
          {
            "date": "...",
            "peer_review": { "TW": {...}, ... },
            "vote": { "TW": +0.1, "US": 0.0, ... },   # 建議調整，範圍 [-0.2, +0.2]
            "summary": {...}
          }
        """
        reports = self._load_reports(date_str)

        peer_review = {}
        votes = {}
        for mkt in self.markets:
            rep = reports.get(mkt)
            if rep is None:
                peer_review[mkt] = {
                    "status": "MISSING",
                    "score": -1.0,
                    "reasons": ["missing_report"],
                }
                votes[mkt] = -0.2  # 缺報告：保守扣分
                continue

            score, reasons = self._score_report(rep)
            peer_review[mkt] = {
                "status": "OK",
                "score": score,
                "reasons": reasons,
                "metrics": self._extract_metrics(rep),
            }
            votes[mkt] = self._score_to_vote(score)

        summary = self._summary(peer_review, votes)

        return {
            "date": date_str,
            "peer_review": peer_review,
            "vote": votes,
            "summary": summary,
        }

    # ---------------- scoring rules ----------------

    @staticmethod
    def _extract_metrics(report: Dict[str, Any]) -> Dict[str, float]:
        """
        允許 report 有 meta/data 包裹（你 report_writer 若有 meta/data 也沒關係）
        """
        data = report.get("data", report)
        def f(key, default=0.0):
            try:
                return float(data.get(key, default))
            except Exception:
                return float(default)

        return {
            "return": f("return", 0.0),
            "drawdown": f("drawdown", 0.0),
            "volatility": f("volatility", 0.0),
            "win_rate": f("win_rate", 0.0),
            "confidence": f("confidence", 0.0),
        }

    def _score_report(self, report: Dict[str, Any]) -> (float, List[str]):
        """
        score 範圍大致落在 [-1.0, +1.0]
        越保守越好：寧可不加分，也不要亂加
        """
        m = self._extract_metrics(report)
        reasons = []

        # 基礎分（0）
        score = 0.0

        # 1) 回撤：越大越扣（drawdown 通常為負數）
        dd = m["drawdown"]
        if dd <= -0.12:
            score -= 0.7; reasons.append("heavy_drawdown")
        elif dd <= -0.08:
            score -= 0.45; reasons.append("high_drawdown")
        elif dd <= -0.05:
            score -= 0.25; reasons.append("moderate_drawdown")
        elif dd >= -0.02:
            score += 0.10; reasons.append("low_drawdown")

        # 2) 波動：越高越扣
        vol = m["volatility"]
        if vol >= 0.035:
            score -= 0.35; reasons.append("very_high_volatility")
        elif vol >= 0.025:
            score -= 0.22; reasons.append("high_volatility")
        elif vol <= 0.012 and vol > 0:
            score += 0.08; reasons.append("low_volatility")

        # 3) 勝率：太低扣，穩定偏高加
        wr = m["win_rate"]
        if wr <= 0.42:
            score -= 0.25; reasons.append("low_win_rate")
        elif wr >= 0.58:
            score += 0.12; reasons.append("good_win_rate")

        # 4) 信心：過低扣（避免模型亂講），中高略加
        cf = m["confidence"]
        if cf <= 0.35:
            score -= 0.25; reasons.append("low_confidence")
        elif cf >= 0.70:
            score += 0.08; reasons.append("high_confidence")

        # 5) 報酬：只給很小權重（避免追高）
        ret = m["return"]
        if ret <= -0.02:
            score -= 0.15; reasons.append("bad_return")
        elif ret >= 0.02:
            score += 0.05; reasons.append("good_return")

        # 限幅
        if score > 1.0: score = 1.0
        if score < -1.0: score = -1.0

        if not reasons:
            reasons.append("neutral")

        return score, reasons

    @staticmethod
    def _score_to_vote(score: float) -> float:
        """
        vote 範圍固定在 [-0.2, +0.2]
        這是「建議調整值」：給 guardian/governance 參考，不能直接改權重
        """
        if score <= -0.60:
            return -0.20
        if score <= -0.30:
            return -0.10
        if score <= -0.10:
            return -0.05
        if score < 0.10:
            return 0.00
        if score < 0.35:
            return +0.05
        if score < 0.60:
            return +0.10
        return +0.15  # 即便很強也不給到 +0.2，避免暴衝

    @staticmethod
    def _summary(peer_review: Dict[str, Any], votes: Dict[str, float]) -> Dict[str, Any]:
        ok = [k for k, v in peer_review.items() if v.get("status") == "OK"]
        missing = [k for k, v in peer_review.items() if v.get("status") != "OK"]

        best = None
        worst = None
        if ok:
            sorted_ok = sorted(ok, key=lambda m: peer_review[m]["score"], reverse=True)
            best = sorted_ok[0]
            worst = sorted_ok[-1]

        return {
            "ok_markets": ok,
            "missing_markets": missing,
            "best": best,
            "worst": worst,
            "vote_sum": round(sum(votes.values()), 4),
        }

    # ---------------- IO ----------------

    def _load_reports(self, date_str: str) -> Dict[str, Dict[str, Any]]:
        """
        讀取 snapshot 目錄內 market 報告
        你可以命名：TW.json / US.json / JP.json / CRYPTO.json
        """
        base = self.snapshot_root / date_str
        reports = {}

        for mkt in self.markets:
            # 接受大小寫與不同命名
            candidates = [
                base / f"{mkt}.json",
                base / f"{mkt.lower()}.json",
                base / f"{mkt.upper()}.json",
            ]
            path = next((p for p in candidates if p.exists()), None)
            if path is None:
                continue

            try:
                reports[mkt] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                # 讀不到就當缺失
                continue

        return reports
