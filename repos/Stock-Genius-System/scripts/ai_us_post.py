# 路徑：Quant-Orchestrator/repos/Stock-Genius-System/scripts/ai_us_post.py

import datetime
from system_state import load_guardian_state
from news_radar import load_news_weights
from safe_yfinance import fetch_us_data
from vault_backtest_writer import write_day0_prediction
from forecast_observer import is_final_run_today

MARKET = "US"

def data_sufficiency_check(stock_data, news_weight):
    required_fields = [
        "mom20", "bias", "vol_ratio", "rsi",
        "macd", "atr", "trend_slope",
        "volatility", "multi_timeframe"
    ]
    for f in required_fields:
        if f not in stock_data:
            return False
    if news_weight is None:
        return False
    return True


def generate_report():
    state = load_guardian_state()
    if state["level"] >= 4:
        return None

    if not is_final_run_today(MARKET):
        return None

    stocks = fetch_us_data()
    news_weights = load_news_weights(MARKET)

    report = []
    for s in stocks:
        if not data_sufficiency_check(s, news_weights.get(s["symbol"])):
            continue

        confidence = s["ai_confidence"]
        if confidence is None:
            continue

        report.append({
            "symbol": s["symbol"],
            "confidence": confidence,
            "data": s
        })

    if not report:
        return "資料不足 / 未開市"

    write_day0_prediction(MARKET, report)
    return report


if __name__ == "__main__":
    generate_report()
