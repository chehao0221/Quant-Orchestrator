def interpret_news(news_weight):
    if news_weight is None:
        return {"score": -0.2, "reason": "no_news"}
    return {"score": news_weight, "reason": "news_signal"}
