from core.risk_policy import load_state, save_state, evaluate_risk, should_recheck_l4
from core.notifier import notify
from datetime import datetime

def run_guardian(vix, news_score):
    state = load_state()
    prev_level = state.get("risk_level", 1)

    level = evaluate_risk(vix, news_score)

    if level == 4:
        if prev_level != 4 or should_recheck_l4(state):
            notify("RED", 
                "Guardian 判定市場進入高風險狀態\n\n"
                "• Stock-Genius / Explorer 已暫停對外輸出\n"
                "• 系統進入全面防禦模式\n\n"
                "將於每 90 分鐘重新評估解除條件"
            )
            state["l4_last_check"] = datetime.utcnow().isoformat()

    elif level == 3 and prev_level != 3:
        notify("YELLOW",
            "市場風險升溫\n\n"
            "• 建議保守解讀 AI 預測\n"
            "• 尚未進入極端狀態"
        )

    elif level <= 2 and prev_level >= 3:
        notify("GREEN",
            "市場風險已回落\n\n"
            "• 系統恢復正常觀測狀態"
        )

    state["risk_level"] = level
    save_state(state)
