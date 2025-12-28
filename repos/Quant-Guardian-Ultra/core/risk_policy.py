from datetime import datetime, timedelta
import json
from pathlib import Path

STATE_FILE = Path("../../shared/state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def evaluate_risk(vix, news_score):
    """
    回傳風險等級 L1~L4
    """
    if vix > 35 or news_score > 0.8:
        return 4
    if vix > 25 or news_score > 0.5:
        return 3
    if vix > 18:
        return 2
    return 1

def should_recheck_l4(state):
    last = state.get("l4_last_check")
    if not last:
        return True
    last = datetime.fromisoformat(last)
    return datetime.utcnow() - last >= timedelta(minutes=90)
