from pathlib import Path
from datetime import datetime
from tools.vault_policy import is_deletable_path
from tools.vault_ai_judge import ai_should_delete

LOG_FILE = Path(r"E:\Quant-Vault\LOG\vault_delete.log")

def log(msg: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def execute_cleanup(file_path: Path, last_read_days: int, top5_count: int):
    if is_deletable_path(file_path) and ai_should_delete(file_path, last_read_days, top5_count):
        try:
            file_path.unlink()
            log(f"DELETED {file_path}")
        except Exception as e:
            log(f"FAILED {file_path} | {e}")
