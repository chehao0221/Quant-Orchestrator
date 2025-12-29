from pathlib import Path
import json
from tools.vault_executor import execute_cleanup

class AIVaultGuard:
    def __init__(self, policy_path: str):
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)

        self.root = Path(self.policy["vault_root"])

    def scan_and_clean(self):
        for zone in self.policy["ai_allowed_delete"]:
            base = self.root / zone
            if not base.exists():
                continue

            for file in base.rglob("*.json"):
                execute_cleanup(
                    file_path=file,
                    last_read_days=999,
                    top5_count=0
                )
