# Vault Backtest Schema（唯一真相）

BACKTEST_SCHEMA = {
    "date": str,              # 預測產生日
    "market": str,            # TW / US
    "horizon": int,           # 預測天數（5）
    "symbols": {
        # "2330.TW": { ... }
    }
}

SYMBOL_SCHEMA = {
    "pred_date": str,
    "pred_price": float,
    "pred_ret": float,

    # N 天後才補
    "actual_price": float | None,
    "actual_ret": float | None,
    "hit": bool | None
}
