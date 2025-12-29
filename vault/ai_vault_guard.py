import json
import time
from pathlib import Path

SECONDS_PER_DAY = 86400
N_DAYS = 180
K_SHORTLIST = 30
TOP5_HISTORY_THRESHOLD = 3

class AIVaultGuard:
    def __init__(self, vault_root):
        self.root = Path(vault_root)

    def _load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    def _recently_used(self, path, days=7):
        return (time.time() - path.stat().st_mtime) < days * SECONDS_PER_DAY

    def _has_newer_version(self, path):
        return path.stat().st_mtime < (time.time() - SECONDS_PER_DAY)

    def should_delete_stock_file(self, file_path: Path):
        if not file_path.is_file():
            return False

        if self._recently_used(file_path):
            return False

        age_days = (time.time() - file_path.stat().st_mtime) / SECONDS_PER_DAY
        if age_days < N_DAYS:
            return False

        parts = file_path.parts
        if "core_watch" in parts:
            return False

        if "shortlist" in parts:
            return False

        if "universe" in parts:
            return True

        if "history" in parts or "cache" in parts:
            return self._has_newer_version(file_path)

        return False

    def cleanup_market(self, market: str):
        base = self.root / "STOCK_DB" / market
        deleted = []

        for folder in ["universe", "history", "cache"]:
            target = base / folder
            if not target.exists():
                continue

            for file in target.rglob("*.json"):
                if self.should_delete_stock_file(file):
                    try:
                        file.unlink()
                        deleted.append(str(file))
                    except:
                        pass

        return deleted
