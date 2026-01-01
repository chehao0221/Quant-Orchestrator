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
