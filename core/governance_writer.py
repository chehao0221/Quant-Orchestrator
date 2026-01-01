# core/governance_writer.py
import json
import os
import time
from pathlib import Path
from typing import Dict

from core.vault_access_guard import VaultAccessGuard


class GovernanceWriter:
    """
    唯一寫入 LOCKED_DECISION 的模組（透過 VaultAccessGuard）
    - ai_weights.json
    - learning_state.json
    - change_log/YYYY-MM-DD.json
    """

    def __init__(self, vault_root: str):
        self.vault_root = vault_root
        self.guard = VaultAccessGuard(vault_root)

    def write_weights_and_state(
        self,
        date_key: str,
        new_weights: Dict,
        new_learning_state: Dict,
        reason: str,
        evidence: Dict,
    ) -> None:
        # 1) weights
        self.guard.write_json(
            role="governance",
            relative_path="LOCKED_DECISION/risk_policy/ai_weights.json",
            payload={"date": date_key, "weights": new_weights},
            reason=reason,
        )

        # 2) learning state
        self.guard.write_json(
            role="governance",
            relative_path="LOCKED_DECISION/horizon/learning_state.json",
            payload=new_learning_state,
            reason=f"{reason}:learning_state",
        )

        # 3) change log（治理證據）
        self.guard.write_json(
            role="governance",
            relative_path=f"LOCKED_DECISION/change_log/{date_key}.json",
            payload={
                "date": date_key,
                "reason": reason,
                "weights": new_weights,
                "learning_state": new_learning_state,
                "evidence": evidence,
            },
            reason=f"{reason}:change_log",
        )
