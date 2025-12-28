# Guardian AI Risk Engine (Full Version)

from datetime import datetime, timedelta
import json
import os

STATE_FILE = "guardian_state.json"

class GuardianEngine:
    def __init__(self):
        self.now = datetime.utcnow()
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        return {
            "risk_level": "L1",
            "status": "GREEN",
            "last_change": None,
            "l4_last_check": None
        }

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    # ===== 核心 AI 判斷（可日後升級）=====
    def ai_risk_assessment(self):
        """
        這裡先用穩定邏輯
        之後你可以接：
        - VIX
        - 黑天鵝事件
        - News Radar
        """
        # ⛔ 現階段：穩定假邏輯（不亂跳）
        return "L3"   # L1~L4 你之後再換成 AI

    def run(self):
        new_level = self.ai_risk_assessment()
        prev_level = self.state["risk_level"]

        # L4 特殊：90 分鐘才允許再次評估解除
        if prev_level == "L4" and new_level != "L4":
            last = self.state.get("l4_last_check")
            if last:
                last = datetime.fromisoformat(last)
                if self.now - last < timedelta(minutes=90):
                    return None  # ⛔ 不發、不變

        changed = new_level != prev_level

        self.state["risk_level"] = new_level
        self.state["status"] = self._map_status(new_level)

        if new_level == "L4":
            self.state["l4_last_check"] = self.now.isoformat()

        if changed:
            self.state["last_change"] = self.now.isoformat()
            self._save_state()
            return self._build_payload(changed=True)

        self._save_state()
        return None

    def _map_status(self, level):
        return {
            "L1": "GREEN",
            "L2": "GREEN",
            "L3": "YELLOW",
            "L4": "RED"
        }[level]

    def _build_payload(self, changed):
        level = self.state["risk_level"]
        status = self.state["status"]

        return {
            "title": "Guardian 風控狀態更新",
            "risk_level": level,
            "status": status,
            "message": self._message(level),
            "timestamp": self.now.isoformat()
        }

    def _message(self, level):
        if level == "L4":
            return "🔴 系統進入全面防禦（不交易）"
        if level == "L3":
            return "🟡 風險升溫，請保守應對"
        return "🟢 市場穩定"
