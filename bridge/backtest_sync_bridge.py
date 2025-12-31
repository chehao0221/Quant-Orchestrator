# backtest_sync_bridge.py
# 回測摘要跨系統同步橋（終極封頂版）
# 職責：
# - 接收 Quant-Orchestrator 回測事實
# - 同步給 Quant-Guardian-Ultra / Stock-Genius-System
# - 作為三系統「事實層」唯一交換通道
# ❌ 不計算 ❌ 不排版 ❌ 不學習 ❌ 不做決策

import json
import os
from typing import Dict, Any
from datetime import datetime


# ===== 環境參數（鐵律，不寫死）=====
GUARDIAN_SYNC_PATH = os.environ.get("GUARDIAN_SYNC_PATH")
GENIUS_SYNC_PATH = os.environ.get("GENIUS_SYNC_PATH")

if not GUARDIAN_SYNC_PATH or not GENIUS_SYNC_PATH:
    raise RuntimeError("🚨 鐵律阻斷：同步路徑環境變數未設定")


# ---------------------------------------------------------------------

def _safe_write(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------

def sync_backtest_summary(
    market: str,
    days: int,
    summary: Dict[str, Any]
) -> None:
    """
    將回測『事實摘要』同步給其他系統
    """

    envelope = {
        "source": "Quant-Orchestrator",
        "market": market,
        "days": days,
        "timestamp": datetime.utcnow().isoformat(),
        "summary": summary
    }

    # 1️⃣ Quant-Guardian-Ultra（風險治理）
    guardian_path = os.path.join(
        GUARDIAN_SYNC_PATH,
        f"{market}_backtest_{days}d.json"
    )
    _safe_write(guardian_path, envelope)

    # 2️⃣ Stock-Genius-System（策略反思）
    genius_path = os.path.join(
        GENIUS_SYNC_PATH,
        f"{market}_backtest_{days}d.json"
    )
    _safe_write(genius_path, envelope)
