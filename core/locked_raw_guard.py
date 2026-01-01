# core/locked_raw_guard.py
import os
import json
import hashlib
import time
from pathlib import Path


class LockedRawViolation(Exception):
    pass


class LockedRawGuard:
    """
    LOCKED_RAW 不可變守門人（append-only）
    - 只允許新增新檔
    - 同名檔案存在就拒絕（禁止覆寫）
    - 原子寫入 + payload hash
    """

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.locked_raw_root = (self.vault_root / "LOCKED_RAW").resolve()
        if not self.locked_raw_root.exists():
            raise LockedRawViolation(f"LOCKED_RAW 不存在: {self.locked_raw_root}")

    def append_json(self, relative_path: str, payload: dict) -> None:
        target = (self.locked_raw_root / relative_path).resolve()
        if not str(target).startswith(str(self.locked_raw_root)):
            raise LockedRawViolation("非法路徑（疑似 path traversal）")

        if target.exists():
            raise LockedRawViolation(f"禁止覆寫 LOCKED_RAW 歷史檔案: {target}")

        target.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "meta": {"timestamp": int(time.time()), "payload_hash": self._hash(payload)},
            "data": payload,
        }
        self._atomic_write_json(target, record)

    @staticmethod
    def _hash(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _atomic_write_json(path: Path, content: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
