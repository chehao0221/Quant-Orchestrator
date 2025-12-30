# Vault 冷資料還原管理器（封頂版）

import os
import zipfile
from datetime import datetime

ARCHIVE_ROOT = r"E:\Quant-Vault\LOCKED_RAW\archive"
AUDIT_LOG = r"E:\Quant-Vault\LOG\vault_deletion_audit.log"

def log(msg: str):
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def restore(zip_name: str, target_dir: str) -> dict:
    zip_path = os.path.join(ARCHIVE_ROOT, zip_name)

    if not os.path.exists(zip_path):
        return {"ok": False, "reason": "ARCHIVE_NOT_FOUND"}

    if "LOCKED_" in target_dir:
        return {"ok": False, "reason": "LOCKED_PATH"}

    with zipfile.ZipFile(zip_path, "r") as z:
        members = z.namelist()
        if len(members) != 1:
            return {"ok": False, "reason": "INVALID_ARCHIVE"}

        filename = members[0]
        target_path = os.path.join(target_dir, filename)

        if os.path.exists(target_path):
            return {"ok": False, "reason": "TARGET_EXISTS"}

        os.makedirs(target_dir, exist_ok=True)
        z.extract(filename, target_dir)

    ts = datetime.utcnow().isoformat()
    log(f"[{ts}] RESTORED: {zip_name} -> {target_path}")

    return {
        "ok": True,
        "restored_to": target_path
    }
