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
# Configuration（封版參數）
# ==================================================

L4_COOLING_HOURS = 3          # L4 最短凍結時間
L4_STABLE_REQUIRED = 2        # 連續穩定次數（90 分鐘一次）

# ==================================================
# AI Risk Scoring（你原本的核心邏輯，完整保留）
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
# Final Risk Decision（含冷卻 + 連續穩定）
# ==================================================

def decide_final_risk_level(
    *,
    current_level: int,
    vix: float,
    sentiment: float,
    event_score: float,
    last_l4_time: Optional[str] = None,
    stable_count: int = 0,
) -> tuple[int, int]:
    """
    回傳：
    - new_level: 最終風險等級
    - new_stable_count: 更新後的穩定次數
    """

    ai_level = evaluate_risk(vix, sentiment, event_score)
    now = datetime.utcnow()

    # === 黑天鵝永遠優先 ===
    if ai_level == 5:
        return 5, 0

    # === 進入 L4（嚴格，不放寬）===
    if ai_level >= 4:
        return 4, 0

    # === L4 狀態下的解凍邏輯 ===
    if current_level == 4:
        # 無 L4 進入時間，保守維持
        if not last_l4_time:
            return 4, 0

        try:
            l4_time = datetime.fromisoformat(last_l4_time)
        except ValueError:
            return 4, 0

        # 冷卻時間尚未結束
        if now < l4_time + timedelta(hours=L4_COOLING_HOURS):
            return 4, 0

        # 冷卻完成後，檢查是否穩定
        if ai_level <= 3:
            stable_count += 1
        else:
            stable_count = 0

        # 連續穩定次數達標 → 允許降級
        if stable_count >= L4_STABLE_REQUIRED:
            return 3, 0

        return 4, stable_count

    # === 非 L4 狀態，直接採用 AI 判斷 ===
    return ai_level, 0
