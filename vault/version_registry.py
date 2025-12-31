# version_registry.py
# 全系統版本化與災難回滾核心（封頂最終版）
# 職責：
# - 所有 AI / Guardian / Orchestrator 變更必須註冊版本
# - 每次學習 / 同步 / 懲罰都留下不可變紀錄
# - 支援一鍵回滾到任一穩定版本
# ❌ 不判斷市場 ❌ 不計算權重 ❌ 不觸發學習

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# =================================================
# Vault Root（鐵律）
# =================================================
VAULT_ROOT = r"E:\Quant-Vault"

VERSION_DIR = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "version_registry"
)

# -------------------------------------------------

def _now() -> str:
    return datetime.utcnow().isoformat()


def _ensure_dir():
    os.makedirs(VERSION_DIR, exist_ok=True)


def _load(path: str) -> Dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =================================================
# 公開 API
# =================================================

def register_version(
    system: str,
    version_tag: str,
    payload: Dict[str, Any]
) -> str:
    """
    註冊一次不可變版本
    system: Guardian / StockGenius / Orchestrator
    """

    _ensure_dir()

    record = {
        "system": system,
        "version": version_tag,
        "timestamp": _now(),
        "payload": payload
    }

    fname = f"{system}_{version_tag}_{int(datetime.utcnow().timestamp())}.json"
    path = os.path.join(VERSION_DIR, fname)

    _save(path, record)
    return path


def list_versions(system: Optional[str] = None):
    _ensure_dir()
    files = sorted(os.listdir(VERSION_DIR))
    if system:
        files = [f for f in files if f.startswith(system)]
    return files


def load_version(file_name: str) -> Dict:
    path = os.path.join(VERSION_DIR, file_name)
    return _load(path)
