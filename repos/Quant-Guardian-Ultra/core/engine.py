import json
from datetime import datetime
from pathlib import Path

from core.risk_policy import (
    decide_final_risk_level,
    RISK_POLICY,
)

# ==================================================
# Guardian Engine（Final）
# ==================================================

class GuardianEngine:
    def __init__(self, state_path: str):
        self.state_path = Path(state_path)
        self.state = self._load_state()

    # --------------------------------------------------
    # State Handling
    # --------------------------------------------------

    def _load_state(self) -> dict:
        if not self.state_path.exists():
            return {
                "level": 1,
                "last_level": None,
                "last_l4_time": None,
                "stable_count": 0,
                "updated_at": None,
            }

        with open(self.state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # 補齊缺失欄位（向後相容）
        state.setdefault("level", 1)
        state.setdefault("last_level", None)
        state.setdefault("last_l4_time", None)
        state.setdefault("stable_count", 0)
        state.setdefault("updated_at", None)

        return state

    def _save_state(self):
        self.state["updated_at"] = datetime.utcnow().isoformat()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # --------------------------------------------------
    # Core Run
    # --------------------------------------------------

    def run(
        self,
        *,
        vix: float,
        sentiment: float,
        event_score: float,
    ) -> dict:
        """
        執行一次 Guardian 風控判斷
        """

        current_level = self.state["level"]

        new_level, new_stable_count = decide_final_risk_level(
            current_level=current_level,
            vix=vix,
            sentiment=sentiment,
            event_score=event_score,
            last_l4_time=self.state.get("last_l4_time"),
            stable_count=self.state.get("stable_count", 0),
        )

        # --------------------------------------------------
        # 狀態轉換處理
        # --------------------------------------------------

        level_changed = new_level != current_level

        if level_changed:
            self.state["last_level"] = current_level
            self.state["level"] = new_level
            self.state["stable_count"] = 0  # 等級變動即重置

            # 記錄 L4 進入時間
            if new_level == 4:
                self.state["last_l4_time"] = datetime.utcnow().isoformat()

            # 離開 L4 時清空時間
            if current_level == 4 and new_level < 4:
                self.state["last_l4_time"] = None

        else:
            # 等級未變，但可能在累積穩定次數
            self.state["stable_count"] = new_stable_count

        self._save_state()

        # --------------------------------------------------
        # 回傳 Payload（給 notifier / workflow 用）
        # --------------------------------------------------

        decision = RISK_POLICY[new_level]

        return {
            "level": decision.level,
            "color": decision.color,
            "description": decision.description,
            "freeze": decision.freeze,
            "level_changed": level_changed,
            "stable_count": self.state["stable_count"],
            "updated_at": self.state["updated_at"],
        }
