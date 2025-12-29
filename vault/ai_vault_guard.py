import os
import time
import json
from pathlib import Path

SECONDS_PER_DAY = 86400

class AIVaultGuard:
    def __init__(self, policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)

        self.vault_root = Path(self.policy["vault_root"])
        self.allowed = self.policy["ai_allowed_delete"]
        self.max_age_days = self.policy["temp_rules"]["max_age_days"]

    def is_safe_path(self, path: Path) -> bool:
        for locked in self.policy["never_delete"]:
            if locked in path.parts:
                return False
        return True

    def should_delete(self, file_path: Path) -> bool:
        if not self.is_safe_path(file_path):
            return False

        try:
            stat = file_path.stat()
        except FileNotFoundError:
            return False

        age_days = (time.time() - stat.st_mtime) / SECONDS_PER_DAY

        # 核心哲學：只在「非常確定安全」時才刪
        if age_days > self.max_age_days:
            return True

        return False

    def execute_cleanup(self):
        deleted = []

        for folder in self.allowed:
            base = self.vault_root / folder
            if not base.exists():
                continue

            for root, _, files in os.walk(base):
                for name in files:
                    path = Path(root) / name
                    if self.should_delete(path):
                        try:
                            path.unlink()
                            deleted.append(str(path))
                        except Exception:
                            pass

        return deleted
