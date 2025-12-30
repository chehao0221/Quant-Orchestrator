def score_stock(stock_data, weights):
    score = 0
    for k, w in weights.items():
        if k in stock_data:
            score += stock_data[k] * w
    return score
