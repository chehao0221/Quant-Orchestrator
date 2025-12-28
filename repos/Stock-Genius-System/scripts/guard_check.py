import json
import sys
from pathlib import Path

STATE_FILE = Path("shared/guardian_state.json")

def check_guardian():
    """
    全系統 Guardian 檢查：
    - L4 以上：直接凍結（exit）
    - L1–L3：正常繼續
    """
    if not STATE_FILE.exists():
        return

    state = json.loads(STATE_FILE.read_text())
    level = state.get("level", 1)
    freeze = state.get("freeze", False)

    if freeze or level >= 4:
        print(f"[Guardian] System frozen at L{level}, exit.")
        sys.exit(0)
