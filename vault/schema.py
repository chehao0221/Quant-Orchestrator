BACKTEST_SYMBOL_SCHEMA = {
    "pred_date": str,
    "pred_price": float,
    "pred_ret": float,
    "actual_price": float | None,
    "actual_ret": float | None,
    "hit": bool | None,
}

BACKTEST_DAY_SCHEMA = {
    "date": str,
    "market": str,
    "horizon": int,
    "symbols": dict,  # symbol -> BACKTEST_SYMBOL_SCHEMA
}
