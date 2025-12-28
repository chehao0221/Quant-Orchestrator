# Guardian AI Risk Engine - AI Level (Step 2)

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

    # ===============================
    # 🧠 AI 風控核心（可持續升級）
    # ===============================
    def ai_risk_score(self):
        score = 0

        # ① 市場波動代理（先用穩定假值）
        market_volatility = 35   # 0~100
        score += market_volatility * 0.4

        # ② 新聞風險（未來接 news_radar）
        news_risk = 30
        score += news_risk * 0.3

        # ③ 黑天鵝歷史相似度
        black_swan_similarity = 20
        score += black_swan_similarity * 0.3

        return int(score)

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
        prev_level = self.state["risk_level"]

        # L4：90 分鐘保護
        if prev_level == "L4" and new_level != "L4":
            last = self.state.get("l4_last_check")
            if last:
                last = datetime.fromisoformat(last)
                if self.now - last < timedelta(minutes=90):
                    return None

        changed = new_level != prev_level

        self.state["risk_level"] = new_level
        self.state["status"] = self._map_status(new_level)

        if new_level == "L4":
            self.state["l4_last_check"] = self.now.isoformat()

        if changed:
            self.state["last_change"] = self.now.isoformat()
            self._save_state()
            return self._build_payload(score)

        self._save_state()
        return None

    def _map_status(self, level):
        return {
            "L1": "GREEN",
            "L2": "GREEN",
            "L3": "YELLOW",
            "L4": "RED"
        }[level]

    def _build_payload(self, score):
        level = self.state["risk_level"]
        return {
            "title": "Guardian AI 風控狀態更新",
            "risk_level": level,
            "status": self.state["status"],
            "message": self._message(level, score),
            "timestamp": self.now.isoformat()
        }

    def _message(self, level, score):
        if level == "L4":
            return f"🔴 AI 判定高風險（Score {score}），系統全面防禦"
        if level == "L3":
            return f"🟡 AI 偵測風險升溫（Score {score}），請保守應對"
        return f"🟢 市場穩定（Score {score}）"
