def consensus(market_score, news_score, stability_score):
    """
    回傳：
    {
        "final_score": float (0-100),
        "confidence_level": "HIGH|MID|LOW",
        "downgrade": bool,
        "note": str
    }
    """

    weights = {
        "market": 0.4,
        "news": 0.3,
        "stability": 0.3
    }

    final = (
        market_score * weights["market"]
        + news_score * weights["news"]
        + stability_score * weights["stability"]
    )

    downgrade = False
    note = ""

    # 防止「單一 AI 拉爆」
    if market_score > 80 and news_score < 30:
        downgrade = True
        note = "⚠️ 技術面強，但消息面不支持"

    if stability_score < 40:
        downgrade = True
        note = "⚠️ 歷史穩定度偏低"

    if final >= 60:
        level = "HIGH"
    elif final >= 30:
        level = "MID"
    else:
        level = "LOW"

    return {
        "final_score": round(final, 1),
        "confidence_level": level,
        "downgrade": downgrade,
        "note": note
    }
