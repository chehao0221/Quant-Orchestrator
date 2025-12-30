import os
from vault_archive_manager import archive_file

def safe_delete(path: str) -> dict:
    if not os.path.exists(path):
        return {"ok": False, "reason": "NOT_FOUND"}

    archive = archive_file(path)
    os.remove(path)

    return {
        "ok": True,
        "deleted": path,
        "archived_to": archive
    }
