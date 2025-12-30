# 冷資料留存裁判 AI（時間衰退版・最終）

import math

def time_decay(age_days: int, half_life: int = 365) -> float:
    """
    指數型時間衰退：
    - age_days = half_life → 價值剩 50%
    """
    return math.exp(-age_days / half_life)

def judge(file_meta: dict) -> dict:
    age = file_meta["age_days"]

    decay = time_decay(age)

    # 基礎保留分數（1 = 非常值得留）
    retain_score = decay

    # 軟性建議（不是硬切）
    recommend_delete = retain_score < 0.25

    return {
        "retain_score": round(retain_score, 4),
        "time_decay": round(decay, 4),
        "recommend_delete": recommend_delete,
        "reason": (
            "TIME_DECAY_LOW"
            if recommend_delete else
            "TIME_DECAY_ACCEPTABLE"
        )
    }
