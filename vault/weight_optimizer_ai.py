# AI 人格演化核心（封頂版）

def optimize(weights: dict, performance_score: float) -> dict:
    lr = 0.05  # 小步長，避免人格崩壞

    if performance_score < 0.5:
        weights["news"] *= (1 - lr)
        weights["technical"] *= (1 - lr / 2)
        weights["guardian_bias"] *= (1 + lr)
    else:
        weights["technical"] *= (1 + lr)
        weights["news"] *= (1 + lr / 2)

    return weights
