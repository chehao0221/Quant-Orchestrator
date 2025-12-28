"""
Quant-Guardian-Ultra
Guardian v2 Entrypoint (Final)

- 支援冷卻時間 / 穩定次數
- 支援 L4 Freeze / L3 Warning
- 狀態唯一寫入 shared/guardian_state.json
- 僅在「等級變化」時通知
"""

from core.engine import GuardianEngine
from core.notifier import Notifier
import random
import os


# ==================================================
# 全系統唯一 Guardian State 位置
# ==================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)
STATE_PATH = os.path.join(BASE_DIR, "shared", "guardian_state.json")


# ==================================================
# Risk Signal Provider（可替換成真實模型）
# ==================================================

def get_risk_signals():
    """
    風控訊號來源（目前為模擬）
    未來可替換：
    - 真實 VIX API
    - 新聞情緒模型（NLP）
    - 黑天鵝事件模型
    """

    return {
        "vix": round(random.uniform(15, 40), 2),
        "sentiment": round(random.uniform(-1.0, 1.0), 3),
        "event_score": round(random.uniform(0.0, 1.0), 3),
    }


# ==================================================
# Main
# ==================================================

def main():
    engine = GuardianEngine(state_path=STATE_PATH)
    notifier = Notifier()

    signals = get_risk_signals()

    payload = engine.run(
        vix=signals["vix"],
        sentiment=signals["sentiment"],
        event_score=signals["event_score"],
    )

    # --------------------------------------------------
    # Console Log（給 workflow / debug 看）
    # --------------------------------------------------

    print(
        "[Guardian]"
        f" Level=L{payload['level']}"
        f" | Freeze={payload['freeze']}"
        f" | StableCount={payload['stable_count']}"
        f" | {payload['description']}"
    )

    # --------------------------------------------------
    # Notify（Notifier 內部會判斷是否需要送）
    # --------------------------------------------------

    notifier.notify(payload)


if __name__ == "__main__":
    main()
