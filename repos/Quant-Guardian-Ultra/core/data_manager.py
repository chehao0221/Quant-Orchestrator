import json
from pathlib import Path
from datetime import datetime
import hashlib


class DataManager:
    """
    Guardian 狀態管理器
    - 管理 state.json
    - 新聞去重
    - 風險狀態持久化
    """

    def __init__(self):
        base_dir = Path(__file__).resolve().parents[1]
        self.data_dir = base_dir / "data"
        self.state_path = self.data_dir / "state.json"

        self.data_dir.mkdir(exist_ok=True)
        self.state = self._load_state()

    # -------------------------------------------------
    # State 基本操作
    # -------------------------------------------------

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 預設 state 結構
        return {
            "risk": {
                "level": "L1",
                "action": "NONE",
                "vix": None,
                "updated_at": None,
            },
            "news_hashes": [],
        }

    def _save_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------
    # 風險狀態
    # -------------------------------------------------

    def update_risk_state(self, level: str, action: str, vix: float):
        self.state["risk"] = {
            "level": level,
            "action": action,
            "vix": vix,
            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        self._save_state()

    def get_risk_state(self) -> dict:
        return self.state.get("risk", {})

    # -------------------------------------------------
    # 新聞去重
    # -------------------------------------------------

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def is_news_seen(self, text: str) -> bool:
        h = self._hash_text(text)
        return h in self.state.get("news_hashes", [])

    def mark_news_seen(self, text: str):
        h = self._hash_text(text)
        if h not in self.state["news_hashes"]:
            self.state["news_hashes"].append(h)
            # 避免無限成長，保留最近 500 筆
            self.state["news_hashes"] = self.state["news_hashes"][-500:]
            self._save_state()
