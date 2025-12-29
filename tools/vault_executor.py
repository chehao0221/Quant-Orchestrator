from pathlib import Path
from datetime import datetime
from vault_policy import is_path_deletable, TEMP_PATH
from vault_ai_judge import ai_should_delete

LOG_FILE = Path(r"E:\Quant-Vault\LOG\vault_delete.log")

def log(msg: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def execute_cleanup():
    for file in TEMP_PATH.rglob("*"):
        try:
            if is_path_deletable(file) and ai_should_delete(file):
                file.unlink()
                log(f"DELETED: {file}")
        except Exception as e:
            log(f"SKIP {file}: {e}")
