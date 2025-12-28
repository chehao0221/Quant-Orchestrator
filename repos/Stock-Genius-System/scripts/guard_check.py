import json
import os
import sys

STATE_FILE = "../../shared/guardian_state.json"

def check_guardian():
    if not os.path.exists(STATE_FILE):
        return True
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    if not state.get("allow_run", True):
        print("⛔ Guardian L4：系統暫停")
        sys.exit(0)

if __name__ == "__main__":
    check_guardian()
