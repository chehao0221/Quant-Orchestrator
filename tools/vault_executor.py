from pathlib import Path
from datetime import datetime
from tools.vault_policy import is_never_delete

LOG_FILE = Path(r"E:\Quant-Vault\LOG\vault_delete.log")

def log(msg: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {msg}\n")

def safe_delete(path: Path):
    if is_never_delete(path):
        log(f"SKIP (NEVER_DELETE): {path}")
        return

    try:
        path.unlink()
        log(f"DELETED: {path}")
    except Exception as e:
        log(f"ERROR: {path} | {e}")
