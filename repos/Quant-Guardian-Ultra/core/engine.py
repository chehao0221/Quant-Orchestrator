from datetime import datetime, timedelta
import json
import os
import csv

STATE_FILE = "../../shared/guardian_state.json"
BLACK_SWAN_FILE = "black_swan_history.csv"
NEWS_CACHE_FILE = "news_cache.json"

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
            "allow_run": True,
            "l4_last_check": None
        }

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    # ===== AI Risk Score =====
    def ai_risk_score(self):
        score = 0
        score += 30 * 0.35  # 市場波動代理
        score += self._news_risk() * 0.35
        score += self._black_swan_risk() * 0.30
        return int(score)

    def _news_risk(self):
        if not os.path.exists(NEWS_CACHE_FILE):
            return 25
        try:
            with open(NEWS_CACHE_FILE, "r") as f:
                return min(80, json.load(f).get("risk_score", 25))
        except:
            return 25

    def _black_swan_risk(self):
        if not os.path.exists(BLACK_SWAN_FILE):
            return 10
        try:
            with open(BLACK_SWAN_FILE) as f:
                return min(70, sum(1 for _ in f) * 8)
        except:
            return 15

    def map_score_to_level(self, score):
        if score >= 76:
            return "L4"
        if score >= 56:
            return "L3"
        if score >= 31:
            return "L2"
        return "L1"

    def run(self):
        score = self.ai_risk_score()
        new_level = self.map_score_to_level(score)
        prev = self.state["risk_level"]

        # L4 冷卻 90 分鐘
        if prev == "L4" and new_level != "L4":
            last = self.state.get("l4_last_check")
            if last:
                last = datetime.fromisoformat(last)
                if self.now - last < timedelta(minutes=90):
                    return None

        if new_level != prev:
            self.state["risk_level"] = new_level
            self.state["status"] = self._map_status(new_level)
            self.state["allow_run"] = new_level != "L4"
            self.state["last_change"] = self.now.isoformat()
            if new_level == "L4":
                self.state["l4_last_check"] = self.now.isoformat()
            self._save_state()
            return self._payload(score)

        self._save_state()
        return None

    def _map_status(self, level):
        return {"L1": "GREEN", "L2": "GREEN", "L3": "YELLOW", "L4": "RED"}[level]

    def _payload(self, score):
        return {
            "title": "Guardian 系統總控狀態",
            "risk_level": self.state["risk_level"],
            "status": self.state["status"],
            "message": self._msg(score),
            "timestamp": self.now.isoformat()
        }

    def _msg(self, score):
        if self.state["risk_level"] == "L4":
            return f"🔴 AI Score {score}\n系統全面防禦，所有分析已凍結"
        if self.state["risk_level"] == "L3":
            return f"🟡 AI Score {score}\n風險升溫，請保守"
        return f"🟢 AI Score {score}\n系統正常"
