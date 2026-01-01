# core/notifier_v2.py
import json
import time
from pathlib import Path
from typing import Dict, Optional
from urllib import request


class NotifierV2:
    """
    可驗證通知：
    - 送出 webhook
    - 記錄 response code / body（節錄）
    - 寫入 TEMP_CACHE/system_audit_state.json 防重複
    """

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.audit_path = self.vault_root / "TEMP_CACHE" / "system_audit_state.json"
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def send(self, webhook_url: str, payload: Dict, context: Optional[Dict] = None) -> Dict:
        context = context or {}
        now = int(time.time())

        # 簡單防重複：同一天同內容不重送
        payload_hash = self._hash(payload)
        audit = self._read_audit()
        last_hash = audit.get("last_payload_hash")
        if last_hash == payload_hash and audit.get("date") == context.get("date"):
            return {"sent": False, "reason": "duplicate", "payload_hash": payload_hash}

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=15) as resp:
                code = int(resp.getcode())
                body = resp.read(500).decode("utf-8", errors="replace")
        except Exception as e:
            result = {"sent": False, "reason": f"error:{e}", "payload_hash": payload_hash}
            self._write_audit({"timestamp": now, "date": context.get("date"), "last_payload_hash": payload_hash, "last_result": result})
            return result

        result = {"sent": (200 <= code < 300), "status_code": code, "body": body, "payload_hash": payload_hash}
        self._write_audit({"timestamp": now, "date": context.get("date"), "last_payload_hash": payload_hash, "last_result": result})
        return result

    def _read_audit(self) -> Dict:
        if not self.audit_path.exists():
            return {}
        try:
            return json.loads(self.audit_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_audit(self, obj: Dict) -> None:
        tmp = self.audit_path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        tmp.replace(self.audit_path)

    @staticmethod
    def _hash(payload: Dict) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        # 不用加密庫也可，但這裡保持簡單穩定
        h = 0
        for ch in raw:
            h = (h * 131 + ord(ch)) % 2_147_483_647
        return str(h)
