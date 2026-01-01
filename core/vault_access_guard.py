# core/vault_access_guard.py
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Literal


class VaultAccessError(Exception):
    """任何未授權的 Vault 存取，直接中止系統"""
    pass


class VaultAccessGuard:
    """
    Quant-Vault 唯一合法寫入守門人
    --------------------------------
    原則：
    1. 只允許寫入 LOCKED_DECISION
    2. 只允許 guardian / governance
    3. 所有寫入都有時間、角色、hash
    """

    ALLOWED_WRITE_ROLES = {"guardian", "governance"}
    ALLOWED_ROOT = "LOCKED_DECISION"

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        if not self.vault_root.exists():
            raise VaultAccessError(f"Quant-Vault 不存在: {self.vault_root}")

    # ---------- public API ----------

    def write_json(
        self,
        role: Literal["guardian", "governance"],
        relative_path: str,
        payload: dict,
        reason: str
    ) -> None:
        """
        唯一合法寫入入口（JSON）
        """

        self._validate_role(role)
        target_path = self._resolve_and_validate_path(relative_path)

        record = {
            "meta": {
                "timestamp": int(time.time()),
                "role": role,
                "reason": reason,
                "payload_hash": self._hash_payload(payload)
            },
            "data": payload
        }

        self._atomic_write_json(target_path, record)

    # ---------- internal guards ----------

    def _validate_role(self, role: str):
        if role not in self.ALLOWED_WRITE_ROLES:
            raise VaultAccessError(
                f"角色 [{role}] 無寫入權限，允許角色: {self.ALLOWED_WRITE_ROLES}"
            )

    def _resolve_and_validate_path(self, relative_path: str) -> Path:
        """
        確保：
        - 寫入目標在 LOCKED_DECISION 底下
        - 不允許 path traversal
        """

        target = (self.vault_root / relative_path).resolve()

        if not str(target).startswith(str(self.vault_root)):
            raise VaultAccessError("非法路徑（疑似 path traversal）")

        if self.ALLOWED_ROOT not in target.parts:
            raise VaultAccessError(
                f"禁止寫入非 {self.ALLOWED_ROOT} 區域: {target}"
            )

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
