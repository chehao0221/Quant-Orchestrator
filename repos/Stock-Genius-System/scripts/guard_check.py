import json
import sys
from pathlib import Path

# 以「本檔案位置」為基準，保證不會迷路
BASE_DIR = Path(__file__).resolve().parents[3]
STATE_FILE = BASE_DIR / "shared" / "guardian_state.json"

def check_guardian(task_type: str = "MARKET"):
    """
    task_type:
    - MARKET   → 市場解讀 / AI 預測 / 發 Discord
    - BACKTEST → 回測 / 歷史分析（Freeze 仍允許）
    """

    if not STATE_FILE.exists():
        return

    try:
        state = json.loads(STATE_FILE.read_text())
    except Exception:
        return

    level = state.get("level", 1)
    freeze = state.get("freeze", False)
    mode = state.get("mode", "HARD")  # 預設 HARD，向下相容

    if freeze and level >= 4 and task_type == "MARKET":
        print(f"[Guardian] HARD FREEZE at L{level}. Skip MARKET task.")
        sys.exit(0)   # 一定是 0
