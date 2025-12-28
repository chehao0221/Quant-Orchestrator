import json, sys, os

STATE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../shared/system_state.json")
)

with open(STATE, "r") as f:
    s = json.load(f)

if s["l4"]["active"]:
    print("⛔ L4 active → skip execution")
    sys.exit(0)

if s["l3"]["active"]:
    os.environ["SYSTEM_RISK"] = "L3"
    print("⚠️ L3 active")
