def adjust_weights(stats):
    """
    stats:
      - market_hit_rate
      - news_hit_rate
      - stability_hit_rate
    """

    weights = {
        "market": 0.4,
        "news": 0.3,
        "stability": 0.3
    }

    for k in weights:
        if stats[k] >= 60:
            weights[k] += 0.02
        elif stats[k] <= 40:
            weights[k] -= 0.02

    total = sum(weights.values())
    for k in weights:
        weights[k] /= total

    return weights
