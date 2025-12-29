from pathlib import Path
from tools.vault_policy import is_never_delete
from tools.vault_ai_judge import is_cold

def try_delete(path: Path, cold_days: int) -> bool:
    if not path.is_file():
        return False
    if is_never_delete(path):
        return False

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return is_cold(mtime, cold_days)
