# 真正的 Day 5 回測裁判（不做預測）

from datetime import datetime

def evaluate_prediction(prediction: dict, actual_price: float) -> dict:
    predicted = prediction["target_price"]
    tolerance = prediction.get("tolerance", 0.03)

    hit = abs(actual_price - predicted) / predicted <= tolerance

    return {
        "hit": hit,
        "predicted": predicted,
        "actual": actual_price,
        "time": datetime.utcnow().isoformat()
    }
