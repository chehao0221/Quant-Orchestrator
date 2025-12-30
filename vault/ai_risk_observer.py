def observe_risk(hit_rate_trend):
    if hit_rate_trend < 0.4:
        return {"penalty": -0.3, "reason": "model_degrading"}
    return {"penalty": 0.0, "reason": "stable"}
