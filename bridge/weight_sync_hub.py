# weight_sync_hub.py
# 三系統 AI 權重同步中樞（封頂最終版）
# 職責：
# - 接收 Learning Gate 產生的「權重變動事實」
# - 同步至 Quant-Guardian-Ultra / Stock-Genius-System
# - 保留 Guardian veto 能力
# ❌ 不做學習 ❌ 不做判斷 ❌ 不產生市場結論

import json
import os
from datetime import datetime
from typing import Dict, Any

from shared.guardian_state import get_guardian_level

# -------------------------------------------------
# 同步目標（三系統共識）
# -------------------------------------------------

SYNC_TARGETS = {
    "ORCHESTRATOR": "vault/weights/global_weights.json",
    "GUARDIAN": "guardian/weights/global_weights.json",
    "STOCK_GENIUS": "repos/Stock-Genius-System/weights/global_weights.json",
}

BLOCK_LEVEL = 4  # Guardian ≥ L4 全面凍結同步


# -------------------------------------------------
# 核心 API
# -------------------------------------------------

def sync_weights(
    market: str,
    delta: Dict[str, Any],
    reason: str
) -> bool:
    """
    同步權重變化（唯一合法入口）
    delta: {"by_indicator": {...}}
    """

    guardian_level = get_guardian_level()
    if guardian_level >= BLOCK_LEVEL:
        return False  # Guardian veto

    payload = {
        "market": market,
        "delta": delta,
        "reason": reason,
        "synced_at": datetime.utcnow().isoformat()
    }

    for name, rel_path in SYNC_TARGETS.items():
        _write_sync_payload(rel_path, payload)

    return True


# -------------------------------------------------
# 內部工具
# -------------------------------------------------

def _write_sync_payload(rel_path: str, payload: Dict[str, Any]) -> None:
    """
    將同步結果寫入指定系統（覆蓋式、可回溯）
    """
    full_path = os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
