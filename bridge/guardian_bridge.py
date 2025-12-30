# Quant-Orchestrator/bridge/guardian_bridge.py
# Guardian ↔ Stock-Genius 橋接器（封頂最終版）

import json
import os
from typing import Optional, Dict, Any

GUARDIAN_STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "shared",
    "guardian_state.json"
)


def fetch_guardian_state() -> Optional[Dict[str, Any]]:
    """
    讀取 Guardian 最終風控結論（唯一路徑）
    回傳格式必須包含：
      - risk_level (L0–L5)
      - confidence (0–1)
      - timestamp
    若資料不存在 / 結構錯誤 → 回傳 None（上層必須中止）
    """

    if not os.path.exists(GUARDIAN_STATE_PATH):
        # Guardian 尚未產生任何結論
        return None

    try:
        with open(GUARDIAN_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # JSON 損毀 / 讀取錯誤
        return None

    # --- 結構完整性檢查（鐵律） ---
    required_fields = {"risk_level", "confidence", "timestamp"}

    if not isinstance(data, dict):
        return None

    if not required_fields.issubset(data.keys()):
        return None

    # --- 值域檢查，避免隱性誤判 ---
    if data["risk_level"] not in {"L0", "L1", "L2", "L3", "L4", "L5"}:
        return None

    try:
        confidence = float(data["confidence"])
    except (TypeError, ValueError):
        return None

    if not (0.0 <= confidence <= 1.0):
        return None

    return {
        "risk_level": data["risk_level"],
        "confidence": confidence,
        "timestamp": data["timestamp"]
    }
