import json
from pathlib import Path
from datetime import datetime
from tools.vault_ai_judge import is_cold

class AIVaultGuard:
    def __init__(self, policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.root = Path(self.cfg["vault_root"])
        self.cold_days = self.cfg["temp_rules"]["cold_days"]

        self.allowed = self.cfg["ai_allowed_delete"]
        self.protected = self.cfg["protected_hot_zones"]

    def _is_protected(self, path: Path):
        return any(p in path.parts for p in self.protected)

    def execute_cleanup(self):
        deleted = []

        for rel in self.allowed:
            base = self.root / rel
            if not base.exists():
                continue

            for file in base.rglob("*.json"):
                if self._is_protected(file):
                    continue

                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if is_cold(mtime, self.cold_days):
                    try:
                        file.unlink()
                        deleted.append(str(file))
                    except Exception:
                        pass

        return deleted
