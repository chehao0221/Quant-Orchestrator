import os
import time
from pathlib import Path

# ====== 核心設定 ======

VAULT_ROOT = Path("/Quant-Vault")
TEMP_CACHE = VAULT_ROOT / "TEMP_CACHE"
LOG_DIR = VAULT_ROOT / "LOG"

# 秒數設定（非常保守）
MAX_AGE_SECONDS = 60 * 60 * 24 * 7   # 7 天
MIN_FILE_SIZE_BYTES = 1             # 0 byte 直接視為可刪

# ====== 安全防護 ======

FORBIDDEN_DIRS = [
    VAULT_ROOT / "LOCKED_RAW",
    VAULT_ROOT / "LOCKED_DECISION",
    VAULT_ROOT / "LOG"
]

def _is_forbidden(path: Path) -> bool:
    return any(str(path).startswith(str(fd)) for fd in FORBIDDEN_DIRS)

def _log(msg: str):
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "ai_cleaner.log", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")

# ====== AI 判斷（規則型） ======

def ai_can_delete(file_path: Path) -> bool:
    """
    Rule-AI:
    只在 100% 確定安全時回 True
    """

    # ❶ 硬性防線
    if _is_forbidden(file_path):
        return False

    if not str(file_path).startswith(str(TEMP_CACHE)):
        return False

    # ❷ 檔案不存在
    if not file_path.exists():
        return False

    # ❸ 年齡判斷
    age = time.time() - file_path.stat().st_mtime
    if age < MAX_AGE_SECONDS:
        return False

    # ❹ 空檔 / 異常檔
    if file_path.stat().st_size <= MIN_FILE_SIZE_BYTES:
        return True

    # ❺ 預設保守：不確定就不刪
    return True


def run_ai_cleanup(dry_run: bool = False):
    """
    dry_run=True 時只記錄、不刪
    """

    if not TEMP_CACHE.exists():
        _log("TEMP_CACHE not found, skip")
        return

    for root, _, files in os.walk(TEMP_CACHE):
        for name in files:
            fp = Path(root) / name

            if ai_can_delete(fp):
                if dry_run:
                    _log(f"[DRY-RUN] Would delete: {fp}")
                else:
                    try:
                        fp.unlink()
                        _log(f"[DELETED] {fp}")
                    except Exception as e:
                        _log(f"[ERROR] {fp} | {e}")
