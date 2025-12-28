import json
import sys
from pathlib import Path

STATE_FILE = Path("shared/state.json")

def main():
    if not STATE_FILE.exists():
        print("[GATE] state.json 不存在，視為安全通過（L1）")
        sys.exit(0)

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    level = state.get("level", "L1")

    print(f"[GATE] Guardian Level = {level}")

    if level in ("L4", "L5", "L6"):
        print("[GATE] 高風險狀態，阻止後續 workflow")
        sys.exit(1)

    print("[GATE] 允許執行後續 workflow")
    sys.exit(0)

if __name__ == "__main__":
    main()
