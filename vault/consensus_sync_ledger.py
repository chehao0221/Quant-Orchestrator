# consensus_sync_ledger.py
# 三系統共識同步審計帳本（封頂最終版）
# 職責：
# - 記錄 Guardian / Stock-Genius / Orchestrator 三方每一次權重或狀態同步
# - 強制共識：未達門檻不可寫入正式狀態
# - 作為「互相學習 × 互相約制 × 可回溯審計」的唯一依據
# ❌ 不計算權重 ❌ 不做市場判斷 ❌ 不觸發學習

import os
import json
from datetime import datetime
from typing import Dict, Any, List

# =================================================
# Vault Root（鐵律）
# =================================================
VAULT_ROOT = r"E:\Quant-Vault"

LEDGER_PATH = os.path.join(
    VAULT_ROOT,
    "LOCKED_DECISION",
    "consensus",
    "sync_ledger.json"
)

# =================================================
# 內部工具
# =================================================

def _now() -> str:
    return datetime.utcnow().isoformat()


def _load() -> List[Dict[str, Any]]:
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(records: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


# =================================================
# 公開 API
# =================================================

def record_consensus(
    market: str,
    guardian_vote: Dict[str, Any],
    stock_genius_vote: Dict[str, Any],
    orchestrator_vote: Dict[str, Any],
    final_action: str
) -> Dict[str, Any]:
    """
    記錄一次三方共識結果
    final_action:
      - APPLY
      - BLOCK
      - SHRINK
      - ROLLBACK
    """

    record = {
        "timestamp": _now(),
        "market": market,
        "guardian": guardian_vote,
        "stock_genius": stock_genius_vote,
        "orchestrator": orchestrator_vote,
        "final_action": final_action
    }

    records = _load()
    records.append(record)
    _save(records)

    return record


def latest_records(limit: int = 20) -> List[Dict[str, Any]]:
    records = _load()
    return records[-limit:]
