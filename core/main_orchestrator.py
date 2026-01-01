# core/main_orchestrator.py
import os
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Literal

from core.council_engine import CouncilEngine
from core.bounded_learning import BoundedLearning
from core.governance_writer import GovernanceWriter
from core.notifier_v2 import NotifierV2

# 你已經有的模組（照你 repo 命名，若不同你再改 import 名稱即可）
from core.evaluation_engine import EvaluationEngine
from core.guardian_v2 import GuardianV2


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class OrchestratorConfig:
    vault_root: str = r"E:\Quant-Vault"
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

        # 2) guardian（決定能否學習）
        guardian_result = self.guardian.run(date_key, eval_scores, eval_evidence)

        # 3) council（互評）
        council_votes = self.council.run(eval_scores, guardian_result.get("state", guardian_result))

        # 4) 讀取現行 ai_weights（若不存在，給預設平均）
        current_weights = self._read_current_weights()

        # 5) bounded learning（提出新權重）
        learning_state = self._read_learning_state()
        proposed_weights, new_learning_state = self.learning.propose_new_weights(
            current_weights=current_weights,
            eval_scores=eval_scores,
            council_votes=council_votes,
            learning_state=learning_state,
            guardian_result=guardian_result,
        )

        # 6) governance 寫入（唯一合法寫入）
        reason = "bounded_learning_update" if proposed_weights != current_weights else "no_change"
        evidence = {
            "eval_scores": eval_scores,
            "council_votes": council_votes,
            "guardian_result": guardian_result,
            "eval_evidence": eval_evidence,
            "before_weights": current_weights,
        }

        # 即使 no_change，也更新 learning_state（記錄 guardian_block/cooldown_block）
        self.gov.write_weights_and_state(
            date_key=date_key,
            new_weights=proposed_weights,
            new_learning_state=new_learning_state,
            reason=reason,
            evidence=evidence,
        )

        # 7) notifier（可驗證回執）
        webhook = os.getenv(self.cfg.webhook_env, "").strip()
        notify_result = {"sent": False, "reason": "no_webhook"}
        if webhook:
            payload = {
                "content": (
                    f"[Quant-Orchestrator] {date_key}\n"
                    f"Guardian: {guardian_result.get('status') or guardian_result.get('decision')}\n"
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
            "eval_scores": eval_scores,
            "council_votes": council_votes,
            "guardian_result": guardian_result,
            "before_weights": current_weights,
            "after_weights": proposed_weights,
            "notify": notify_result,
        }

    # -------- vault readers (read-only) --------

    def _read_current_weights(self) -> Dict[Market, float]:
        p = Path(self.vault_root) / "LOCKED_DECISION" / "risk_policy" / "ai_weights.json"
        markets = ["TW", "US", "JP", "CRYPTO"]
        if p.exists():
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                w = obj.get("weights", obj)
                out = {m: float(w.get(m, 0.0)) for m in markets}
                s = sum(out.values())
                if s > 0:
                    return {m: out[m] / s for m in markets}
            except Exception:
                pass
        return {m: 1.0 / len(markets) for m in markets}

    def _read_learning_state(self) -> Dict:
        p = Path(self.vault_root) / "LOCKED_DECISION" / "horizon" / "learning_state.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}


if __name__ == "__main__":
    result = MainOrchestrator().run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
