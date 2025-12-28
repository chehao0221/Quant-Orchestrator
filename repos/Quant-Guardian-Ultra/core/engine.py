import json
import os
from pathlib import Path
from core.risk_policy import evaluate_risk, RISK_POLICY
from core.notifier import Notifier

STATE_FILE = Path("shared/guardian_state.json")

class GuardianEngine:
    def __init__(self):
        self.notifier = Notifier()
        self.state = self._load_state()

    def _load_state(self):
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return {
            "level": 1,
            "freeze": False
        }

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    def run(self, vix, sentiment, event_score):
        new_level = evaluate_risk(vix, sentiment, event_score)
        old_level = self.state["level"]

        decision = RISK_POLICY[new_level]

        changed = new_level != old_level

        self.state["level"] = new_level
        self.state["freeze"] = decision.freeze

        self._save_state()

        self.notifier.notify(new_level, decision, changed)

        return decision
