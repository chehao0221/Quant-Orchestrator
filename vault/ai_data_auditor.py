# 資料品質審計 AI：判斷「有沒有資格下結論」

def audit(data_profile: dict):
    issues = []

    if data_profile.get("history_days", 0) < 60:
        issues.append("history_too_short")

    if data_profile.get("indicator_count", 0) < 8:
        issues.append("insufficient_indicators")

    if data_profile.get("news_sources", 0) < 2:
        issues.append("single_news_source")

    if issues:
        return {
            "veto": True,
            "reason": ",".join(issues)
        }

    return {
        "veto": False,
        "reason": "data_ok"
    }
