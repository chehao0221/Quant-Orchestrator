import json
import sys
from pathlib import Path

# 以「本檔案位置」為基準，保證不會迷路
BASE_DIR = Path(__file__).resolve().parents[3]
STATE_FILE = BASE_DIR / "shared" / "guardian_state.json"

def check_guardian():
    """
    全系統 Guardian 檢查：
    - L4 以上：直接凍結（exit 0）
    - L1–L3：正常繼續
    """
    if not STATE_FILE.exists():
        # 沒有 Guardian 狀態 → 保守允許執行
        return

    try:
        state = json.loads(STATE_FILE.read_text())
    except Exception:
        # 狀態壞掉 → 保守允許執行
        return

    level = state.get("level", 1)
    freeze = state.get("freeze", False)

    if freeze or level >= 4:
        print(f"[Guardian] System frozen at L{level}. Skip execution.")
        sys.exit(0)   # ⚠️ 一定是 0，不是 error
