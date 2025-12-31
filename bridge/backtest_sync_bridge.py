# backtest_sync_bridge.py
# 回測結果跨系統同步橋（終極封頂版）
# 職責：
# - 接收 Quant-Orchestrator 回測摘要
# - 同步給 Quant-Guardian-Ultra / Stock-Genius-System
# - 僅做資料傳遞與版本標記
# ❌ 不計算 ❌ 不學習 ❌ 不決策 ❌ 不寫死路徑

import os
import json
from datetime import datetime
from typing import Dict, Any

# =================================================
# 環境變數（鐵律）
# =================================================

GUARDIAN_SYNC_PATH = os.environ.get("GUARDIAN_SYNC_PATH")
GENIUS_SYNC_PATH = os.environ.get("GENIUS_SYNC_PATH")

if not GUARDIAN_SYNC_PATH or not GENIUS_SYNC_PATH:
    raise RuntimeError("🚨 鐵律阻斷：同步系統路徑環境變數未設定")

# =================================================
# 工具
# =================================================

def _safe_write(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

# =================================================
# 公開 API
# =================================================

def sync_backtest_summary(
    market: str,
    days: int,
    summary: Dict[str, Any]
) -> None:
    """
    同步回測摘要給 Guardian / Genius
    """

    envelope = {
        "source": "Quant-Orchestrator",
        "market": market,
        "window_days": days,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": summary
    }

    guardian_path = os.path.join(
        GUARDIAN_SYNC_PATH,
        f"backtest_{market}_{days}D.json"
    )

    genius_path = os.path.join(
        GENIUS_SYNC_PATH,
        f"backtest_{market}_{days}D.json"
    )

    _safe_write(guardian_path, envelope)
    _safe_write(genius_path, envelope)
