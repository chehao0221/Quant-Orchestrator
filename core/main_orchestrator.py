# core/main_orchestrator.py
import os
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

from core.council_engine import CouncilEngine
from core.bounded_learning import BoundedLearning
from core.governance_writer import GovernanceWriter
from core.notifier_v2 import NotifierV2
from core.evaluation_engine import EvaluationEngine
from core.guardian_v2 import GuardianV2


@dataclass(frozen=True)
class OrchestratorConfig:
    vault_root: str = "E:/Quant-Vault"  # 你已指定 E:\Quant-Vault
    webhook_env: str = "DISCORD_WEBHOOK_URL"


class MainOrchestrator:
    def __init__(self, cfg: OrchestratorConfig | None = None):
        self.cfg = cfg or OrchestratorConfig()
        self.vault_root = self.cfg.vault_root

        self.evaluator = EvaluationEngine(self.vault_root)
        self.council = CouncilEngine()
        self.guardian = GuardianV2(self.vault_root)
        self.learning = BoundedLearning()
        self.gov = GovernanceWriter(self.vault_root)
        self.notifier = NotifierV2(self.vault_root)

    def run(self) -> Dict:
        date_key = datetime.now().strftime("%Y-%m-%d")

        # 1) evaluation（只讀）
        eval_scores, eval_evidence = self.evaluator.run(date_key)

        # 2) guardian（決定 freeze 狀態）
        guardian_result = self.guardian.run(date_key, eval_scores, eval_evidence)

        # 3) council（互評）
        council_votes = self.council.run(eval_scores, guardian_result)

        # 4) current weights
        current_weights = self._read_current_weights()

        # 5) bounded learning（提出新權重）
        learning_state = self._read_learning_state()
        proposed_weights, new_learning_state, reason, evidence = self.learning.propose(
            date_key=date_key,
            current_weights=current_weights,
            eval_scores=eval_scores,
            council_votes=council_votes,
            guardian_state=guardian_result,
            learning_state=learning_state,
        )

        # 6) governance 寫入（唯一合法寫入 LOCKED_DECISION）
        self.gov.write_weights_and_state(
            date_key=date_key,
            new_weights=proposed_weights,
            new_learning_state=new_learning_state,
            reason=reason,
            evidence={
                "guardian": guardian_result,
                "eval_evidence": eval_evidence,
                "learning_evidence": evidence,
            },
        )

        # 7) notifier（可驗證回執）
        webhook = os.getenv(self.cfg.webhook_env, "").strip()
        notify_result = {"sent": False, "reason": "no_webhook"}
        if webhook:
            payload = {
                "content": (
                    f"[Quant-Orchestrator] {date_key}\n"
                    f"Guardian: {guardian_result.get('status')}\n"
                    f"Eval: {eval_scores}\n"
                    f"Votes: {council_votes}\n"
                    f"Weights: {proposed_weights}\n"
                )
            }
            notify_result = self.notifier.send(
                webhook_url=webhook,
                payload=payload,
                context={"date": date_key, "reason": reason},
            )

        return {
            "date": date_key,
            "guardian": guardian_result,
            "eval_scores": eval_scores,
            "council_votes": council_votes,
            "current_weights": current_weights,
            "proposed_weights": proposed_weights,
            "notify": notify_result,
        }

    def _read_current_weights(self) -> Dict:
        p = Path(self.vault_root) / "LOCKED_DECISION" / "risk_policy" / "ai_weights.json"
        if not p.exists():
            return {"TW": 0.25, "US": 0.25, "JP": 0.25, "CRYPTO": 0.25}
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            data = raw.get("data", raw)
            w = (data.get("weights") if isinstance(data, dict) else None) or {}
            if not w:
                return {"TW": 0.25, "US": 0.25, "JP": 0.25, "CRYPTO": 0.25}
            return w
        except Exception:
            return {"TW": 0.25, "US": 0.25, "JP": 0.25, "CRYPTO": 0.25}

    def _read_learning_state(self) -> Dict:
        p = Path(self.vault_root) / "LOCKED_DECISION" / "horizon" / "learning_state.json"
        if not p.exists():
            return {}
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            return raw.get("data", raw) if isinstance(raw, dict) else {}
        except Exception:
            return {}


if __name__ == "__main__":
    result = MainOrchestrator().run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
