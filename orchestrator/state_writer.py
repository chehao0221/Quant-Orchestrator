import json, os
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(__file__)
STATE = os.path.abspath(os.path.join(BASE, "../shared/system_state.json"))

# Guardian 的 flag（不用改 Guardian）
GUARDIAN_L4_FLAG = os.path.abspath(
    os.path.join(BASE, "../repos/Quant-Guardian-Ultra/data/l4_active.flag")
)

TZ = timezone(timedelta(hours=8))

def load_state():
    with open(STATE, "r") as f:
        return json.load(f)

def save_state(s):
    s["updated_at"] = datetime.now(TZ).isoformat()
    s["source"]["last_writer"] = "guardian"
    with open(STATE, "w") as f:
        json.dump(s, f, indent=2)

def main():
    s = load_state()

    if os.path.exists(GUARDIAN_L4_FLAG):
        s["risk_level"] = 4
        s["l4"]["active"] = True

    save_state(s)

if __name__ == "__main__":
    main()
