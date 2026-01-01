# core/notifier_v2.py
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests


@dataclass(frozen=True)
class NotifierConfig:
    webhook_env: str = "DISCORD_WEBHOOK_URL"
    timeout_sec: int = 10
    max_retries: int = 3
    backoff_sec: float = 1.5


class NotifierV2:
    """
    可驗證通知：
    - payload hash（防重複）
    - response code 記錄（回執）
    - retry + backoff
    """

    def __init__(self, vault_root: str, config: NotifierConfig | None = None):
        self.vault_root = Path(vault_root).resolve()
        self.cfg = config or NotifierConfig()
        self.audit_path = self.vault_root / "TEMP_CACHE" / "system_audit_state.json"
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def send(self, webhook_url: str, payload: Dict, context: Dict) -> Dict:
        payload_hash = self._hash(payload)
        audit = self._load_audit()

        # 防重複（同 hash 不再發）
        last_hash = audit.get("last_payload_hash")
        if last_hash == payload_hash:
            return {"sent": False, "reason": "dedup", "payload_hash": payload_hash, "audit": audit}

        # 送出（含 retry）
        resp_info = None
        ok = False
        for i in range(1, self.cfg.max_retries + 1):
            try:
                r = requests.post(webhook_url, json=payload, timeout=self.cfg.timeout_sec)
                resp_info = {"status_code": r.status_code, "text": (r.text or "")[:500]}
                if 200 <= r.status_code < 300:
                    ok = True
                    break
            except Exception as e:
                resp_info = {"error": str(e)}
            time.sleep(self.cfg.backoff_sec * i)

        # 寫回 audit（回執）
        new_audit = {
            "last_payload_hash": payload_hash if ok else last_hash,
            "last_attempt_ts": int(time.time()),
            "last_ok": ok,
            "last_response": resp_info,
            "context": context,
        }
        self._save_audit(new_audit)

        return {"sent": ok, "payload_hash": payload_hash, "response": resp_info, "audit": new_audit}

    def _load_audit(self) -> Dict:
        if self.audit_path.exists():
            try:
                return json.loads(self.audit_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_audit(self, audit: Dict) -> None:
        tmp = self.audit_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.audit_path)

    @staticmethod
    def _hash(payload: Dict) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
