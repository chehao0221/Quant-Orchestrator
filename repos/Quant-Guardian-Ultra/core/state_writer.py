import json
from pathlib import Path
from datetime import datetime, timezone


STATE_PATH = Path("shared/guardian_state.json")


def write_guardian_state(level: str, action: str, pause_all: bool, notes: str):
    if level in ("L1", "L2"):
        color = "GREEN"
    elif level == "L3":
        color = "YELLOW"
    else:
        color = "RED"

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "global": {
            "level": level,
            "color": color,
            "action": action,
            "pause_all": pause_all
        },
        "markets": {
            "TW": {
                "paused": pause_all or level in ("L4", "L5", "L6"),
                "reason": f"{level} 風控判定",
                "color": color
            },
            "US": {
                "paused": pause_all or level in ("L4", "L5", "L6"),
                "reason": f"{level} 風控判定",
                "color": color
            }
        },
        "notes": notes,
        "source": "Quant-Guardian-Ultra"
    }

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[GUARDIAN] 已寫入 {STATE_PATH.resolve()}")
