from dataclasses import dataclass

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

def evaluate_risk(vix: float, sentiment: float, event_score: float) -> int:
    """
    AI 風控核心邏輯（可後續換模型）
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
