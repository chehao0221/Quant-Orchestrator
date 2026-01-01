# core/locked_raw_guard.py
import os
import json
import hashlib
import time
from pathlib import Path


class LockedRawViolation(Exception):
    """任何試圖修改 LOCKED_RAW 歷史的行為，直接中止"""
    pass


class LockedRawGuard:
    """
    LOCKED_RAW 不可變守門人
    -----------------------
    原則：
    1. 只允許新增（append-only）
    2. 既有檔案不可覆寫
    3. 每筆資料都留下 hash 指紋
    """

    LOCKED_RAW_DIR = "LOCKED_RAW"

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.locked_raw_root = (self.vault_root / self.LOCKED_RAW_DIR).resolve()

        if not self.locked_raw_root.exists():
            raise LockedRawViolation(
                f"LOCKED_RAW 不存在: {self.locked_raw_root}"
            )

    # ---------- public API ----------

    def append_json(self, relative_path: str, payload: dict) -> None:
        """
        唯一合法寫入 LOCKED_RAW 的方式（新增）
        """

        target_path = self._resolve_and_validate_path(relative_path)

        if target_path.exists():
            raise LockedRawViolation(
                f"禁止覆寫 LOCKED_RAW 歷史檔案: {target_path}"
            )

        record = {
            "meta": {
                "timestamp": int(time.time()),
                "payload_hash": self._hash_payload(payload)
            },
            "data": payload
        }

        self._atomic_write_json(target_path, record)

    # ---------- internal guards ----------

    def _resolve_and_validate_path(self, relative_path: str) -> Path:
        """
        確保：
        - 寫入目標一定在 LOCKED_RAW 底下
        - 防止 path traversal
        """

        target = (self.locked_raw_root / relative_path).resolve()

        if not str(target).startswith(str(self.locked_raw_root)):
            raise LockedRawViolation("非法路徑（疑似 path traversal）")

        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    # ---------- utils ----------

    @staticmethod
    def _hash_payload(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _atomic_write_json(path: Path, content: dict):
        """
        原子寫入，避免半寫狀態
        """
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, path)
