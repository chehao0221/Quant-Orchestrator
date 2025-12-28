import json
import sys
from pathlib import Path

STATE_PATH = Path("shared/guardian_state.json")

def main():
    if not STATE_PATH.exists():
        print("[GATE] 找不到 guardian_state.json → 視為安全，允許執行")
        sys.exit(0)

    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[GATE] 狀態檔讀取失敗：{e} → 阻擋執行")
        sys.exit(1)

    level = state.get("level")

    print(f"[GATE] Guardian 狀態等級：{level}")

    if level in ("L4", "L5", "L6"):
        print("[GATE] 🛑 Guardian 判定停盤 → 阻擋 Stock-Genius / Explorer")
        sys.exit(1)

    print("[GATE] ✅ 允許執行")
    sys.exit(0)


if __name__ == "__main__":
    main()
