from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

# ==================================================
# Risk Decision Definition
# ==================================================

@dataclass
class RiskDecision:
    level: int
    color: str
    description: str
    freeze: bool


RISK_POLICY = {
    0: RiskDecision(0, "GREEN", "系統靜默", False),
    1: RiskDecision(1, "GREEN", "市場正常", False),
    2: RiskDecision(2, "GREEN", "市場穩定偏多", False),
    3: RiskDecision(3, "YELLOW", "風險升溫", False),
    4: RiskDecision(4, "RED", "高風險，系統凍結", True),
    5: RiskDecision(5, "RED", "黑天鵝事件", True),
}

# ==================================================
# Configuration
# ==================================================

L4_COOLING_HOURS = 3  # L4 最短凍結時間（小時）

# ==================================================
# AI Risk Scoring (原本邏輯，保留)
# ==================================================

def evaluate_risk(vix: float, sentiment: float, event_score: float) -> int:
    """
    AI 風控核心邏輯（可後續換模型）
    回傳建議風險等級（1~5）
    """
    score = 0

    if vix > 30:
        score += 2
    if sentiment < -0.5:
        score += 2
    if event_score > 0.85:
        score += 2

    if score >= 5:
        return 5
    if score >= 4:
        return 4
    if score >= 3:
        return 3
    if score >= 2:
        return 2
    return 1


# ==================================================
# Final Risk Level Decision (含冷卻時間)
# ==================================================

def decide_final_risk_level(
    *,
    current_level: int,
    vix: float,
    sentiment: float,
    event_score: float,
    last_l4_time: Optional[str] = None,
) -> int:
    """
    綜合 AI 判斷 + 冷卻時間，決定最終風險等級
    """

    ai_level = evaluate_risk(vix, sentiment, event_score)
    now = datetime.utcnow()

    # === 黑天鵝永遠優先 ===
    if ai_level == 5:
        return 5

    # === 進入 L4（嚴格，不放寬）===
    if ai_level >= 4:
        return 4

    # === L4 冷卻邏輯（只影響降級）===
    if current_level == 4:
        # 沒有時間記錄，保守處理
        if not last_l4_time:
            return 4

        try:
            l4_time = datetime.fromisoformat(last_l4_time)
        except ValueError:
            return 4

        # 冷卻時間尚未結束
        if now < l4_time + timedelta(hours=L4_COOLING_HOURS):
            return 4

        # 冷卻完成，只要「沒有繼續惡化」即可降到 L3
        if ai_level <= 3:
            return 3

        return 4

    # === 其他情況：採用 AI 判斷 ===
    return ai_level
