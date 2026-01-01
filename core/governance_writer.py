# core/governance_writer.py
import json
from dataclasses import dataclass
from typing import Dict, Literal

from core.vault_access_guard import VaultAccessGuard


Market = Literal["TW", "US", "JP", "CRYPTO"]


@dataclass(frozen=True)
class GovernancePaths:
    ai_weights: str = "LOCKED_DECISION/risk_policy/ai_weights.json"
    learning_state: str = "LOCKED_DECISION/horizon/learning_state.json"
    change_log_dir: str = "LOCKED_DECISION/change_log"


class GovernanceWriter:
    """
    唯一合法寫入 LOCKED_DECISION 的治理寫手（透過 VaultAccessGuard）
    - 更新 ai_weights.json
    - 更新 learning_state.json
    - 寫入 change_log/YYY-MM-DD_xxx.json
    """

    def __init__(self, vault_root: str):
        self.guard = VaultAccessGuard(vault_root)
        self.paths = GovernancePaths()

    def write_weights_and_state(
        self,
        date_key: str,
        new_weights: Dict[Market, float],
        new_learning_state: Dict,
        reason: str,
        evidence: Dict,
    ) -> None:
        # 1) ai_weights
        self.guard.write_json(
            role="governance",
            relative_path=self.paths.ai_weights,
            payload={"weights": new_weights, "date": date_key},
            reason=reason,
        )

        # 2) learning_state
        self.guard.write_json(
            role="governance",
            relative_path=self.paths.learning_state,
            payload=new_learning_state,
            reason=reason,
        )

        # 3) change log（不可少）
        change_log_path = f"{self.paths.change_log_dir}/{date_key}.json"
        payload = {
            "date": date_key,
            "reason": reason,
            "evidence": evidence,
            "after": {"weights": new_weights, "learning_state": new_learning_state},
        }
        self.guard.write_json(
            role="governance",
            relative_path=change_log_path,
            payload=payload,
            reason="governance_change_log",
        )
