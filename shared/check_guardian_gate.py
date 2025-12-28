import json
import sys
from pathlib import Path

STATE_PATH = Path(__file__).parent / "guardian_state.json"

def main():
    if not STATE_PATH.exists():
        print("[GATE] guardian_state.json 不存在 → 視為安全，允許執行")
        return 0

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    level = state.get("level", "L1")

    print(f"[GATE] Guardian Level = {level}")

    # 硬停條件
    if level in ["L4", "BLACK", "BLACK_SWAN"]:
        print("🛑 Guardian 判定極端風險，Genius workflow 已暫停")
        return 99

    print("✅ Guardian 允許 Genius 繼續執行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
