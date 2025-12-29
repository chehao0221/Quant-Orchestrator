import time
import json
from pathlib import Path

SECONDS_PER_DAY = 86400

class AIVaultGuard:
    def __init__(self, policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)

        self.root = Path(self.policy["vault_root"])
        self.cold_days = self.policy["temp_rules"]["cold_days"]
        self.read_protect_days = self.policy["temp_rules"]["insurance_read_days"]

        self.allowed = [self.root / p for p in self.policy["ai_allowed_delete"]]
        self.protected = [self.root / p for p in self.policy["protected_hot_zones"]]

    def is_protected(self, path: Path) -> bool:
        return any(p in path.parents for p in self.protected)

    def is_allowed(self, path: Path) -> bool:
        return any(a in path.parents for a in self.allowed)

    def is_cold(self, path: Path) -> bool:
        age_days = (time.time() - path.stat().st_mtime) / SECONDS_PER_DAY
        return age_days >= self.cold_days

    def recently_used(self, path: Path) -> bool:
        age_days = (time.time() - path.stat().st_atime) / SECONDS_PER_DAY
        return age_days <= self.read_protect_days

    def should_delete(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if self.is_protected(path):
            return False
        if not self.is_allowed(path):
            return False
        if self.recently_used(path):
            return False
        if not self.is_cold(path):
            return False
        return True

    def execute_cleanup(self):
        deleted = []
        for base in self.allowed:
            if not base.exists():
                continue
            for file in base.rglob("*.json"):
                if self.should_delete(file):
                    try:
                        file.unlink()
                        deleted.append(str(file))
                    except:
                        pass
        return deleted
