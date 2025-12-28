import json
import sys
from pathlib import Path


STATE_PATH = Path("shared/guardian_state.json")
MARKET = sys.argv[1] if len(sys.argv) > 1 else "GLOBAL"


def main():
    if not STATE_PATH.exists():
        print("[GATE] 找不到 guardian_state.json，預設放行")
        sys.exit(0)

    with STATE_PATH.open("r", encoding="utf-8") as f:
        state = json.load(f)

    level = state["global"]["level"]
    color = state["global"]["color"]

    if MARKET == "GLOBAL":
        paused = state["global"]["pause_all"]
    else:
        paused = state["markets"].get(MARKET, {}).get("paused", False)

    print(f"[GATE] Level={level} Color={color} Market={MARKET} Paused={paused}")

    if paused:
        print("🛑 Guardian 判定今日停盤")
        sys.exit(1)

    print("✅ Guardian 放行")
    sys.exit(0)


if __name__ == "__main__":
    main()
