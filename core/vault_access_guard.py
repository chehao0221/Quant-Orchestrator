# core/vault_access_guard.py
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Literal


class VaultAccessError(Exception):
    pass


class VaultAccessGuard:
    """
    Quant-Vault 寫入守門人（唯一合法寫入入口）
    - 只允許寫入 LOCKED_DECISION/**
    - 只允許角色 guardian / governance
    - 原子寫入 + payload hash + reason
    """

    ALLOWED_WRITE_ROLES = {"guardian", "governance"}

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        if not self.vault_root.exists():
            raise VaultAccessError(f"Quant-Vault 不存在: {self.vault_root}")

    def write_json(
        self,
        role: Literal["guardian", "governance"],
        relative_path: str,
        payload: dict,
        reason: str,
    ) -> None:
        self._validate_role(role)
        target = self._resolve_locked_decision_path(relative_path)

        record = {
            "meta": {
                "timestamp": int(time.time()),
                "role": role,
                "reason": reason,
                "payload_hash": self._hash_payload(payload),
            },
            "data": payload,
        }
        self._atomic_write_json(target, record)

    def _validate_role(self, role: str) -> None:
        if role not in self.ALLOWED_WRITE_ROLES:
            raise VaultAccessError(
                f"角色 [{role}] 無寫入權限，允許角色: {sorted(self.ALLOWED_WRITE_ROLES)}"
            )

    def _resolve_locked_decision_path(self, relative_path: str) -> Path:
        target = (self.vault_root / relative_path).resolve()

        # 防 path traversal
        if not str(target).startswith(str(self.vault_root)):
            raise VaultAccessError("非法路徑（疑似 path traversal）")

        # 必須寫入 LOCKED_DECISION
        if "LOCKED_DECISION" not in target.parts:
            raise VaultAccessError(f"禁止寫入非 LOCKED_DECISION 區域: {target}")

        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    @staticmethod
    def _hash_payload(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _atomic_write_json(path: Path, content: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
