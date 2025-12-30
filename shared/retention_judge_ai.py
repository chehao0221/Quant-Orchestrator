# 冷資料留存裁判 AI（不刪檔）

def judge(file_meta: dict) -> dict:
    score = 1.0

    if file_meta["age_days"] > 365:
        score -= 0.4
    if file_meta["age_days"] > 720:
        score -= 0.3

    score = max(score, 0)

    return {
        "retain_score": score,
        "recommend_delete": score < 0.3,
        "reason": "LONG_TERM_UNUSED" if score < 0.3 else "KEEP"
    }
