import json
import os

STATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "guardian_state.json"
)

def load_guardian_state():
    if not os.path.exists(STATE_PATH):
        return {"level": "L0"}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
