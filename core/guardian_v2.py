# core/guardian_v2.py
import json
from pathlib import Path
from typing import Dict, Literal


Market = Literal["TW", "US", "JP", "CRYPTO"]


class GuardianV2:
    """
    Guardian V2（雙層）
    - 硬規則：低分/缺報告 => FREEZE
    - 軟規則：狀態輸出供 council / learning 使用
    ※ Guardian 本身「不寫入」Vault（寫入由 GovernanceWriter 統一處理）
    """

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.guardian_state_path = (
            self.vault_root / "LOCKED_DECISION" / "guardian" / "guardian_state.json"
        )

        # 你可日後調整，但這版先給「終極保守」
        self.min_score = 0.35  # 低於此分 => freeze
        self.missing_report_freeze = True

    def run(self, date_key: str, eval_scores: Dict[Market, float], eval_evidence: Dict) -> Dict:
        prev_state = self._read_prev_state()

        markets = ["TW", "US", "JP", "CRYPTO"]
        freeze = {m: False for m in markets}
        reasons = {}

        for m in markets:
            s = float(eval_scores.get(m, 0.0))
            ev = eval_evidence.get(m, {})
            if self.missing_report_freeze and isinstance(ev, dict) and ev.get("reason", "").startswith("missing_report"):
                freeze[m] = True
                reasons[m] = ev.get("reason")
                continue

            if s < self.min_score:
                freeze[m] = True
                reasons[m] = f"score<{self.min_score}: {s:.4f}"

        # 全市場都 freeze -> 系統 freeze
        all_freeze = all(freeze.values())

        status = "PASS"
        if all_freeze:
            status = "FREEZE_ALL"
        elif any(freeze.values()):
            status = "FREEZE_PARTIAL"

        out = {
            "date": date_key,
            "status": status,
            "freeze": freeze,
            "reasons": reasons,
            "prev_state": prev_state,
        }
        return out

    def _read_prev_state(self) -> Dict:
        if not self.guardian_state_path.exists():
            return {}
        try:
            raw = json.loads(self.guardian_state_path.read_text(encoding="utf-8"))
            return raw.get("data", raw)
        except Exception:
            return {}
