import json
from pathlib import Path
from core.risk_policy import evaluate_risk, RISK_POLICY
from core.notifier import Notifier

STATE_FILE = Path("shared/guardian_state.json")

DEFAULT_STATE = {
    "level": 1,
    "freeze": False
}

class GuardianEngine:
    def __init__(self):
        self.notifier = Notifier()
        self.state = self._load_state()

    def _load_state(self):
        # 檔案不存在 → 用預設
        if not STATE_FILE.exists():
            return DEFAULT_STATE.copy()

        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            return DEFAULT_STATE.copy()

        # 🔑 自我修復（關鍵）
        for k, v in DEFAULT_STATE.items():
            if k not in state:
                state[k] = v

        return state

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    def run(self, vix, sentiment, event_score):
        new_level = evaluate_risk(vix, sentiment, event_score)
        old_level = self.state.get("level", DEFAULT_STATE["level"])

        decision = RISK_POLICY[new_level]
        changed = new_level != old_level

        self.state["level"] = new_level
        self.state["freeze"] = decision.freeze

        self._save_state()

        self.notifier.notify(new_level, decision, changed)

        return decision
