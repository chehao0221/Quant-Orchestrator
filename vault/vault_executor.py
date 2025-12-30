"""
統一 Vault 寫入入口（給 AI / 上層用）
"""

from vault_snapshot_writer import write_snapshot
from vault_event_store import write_event
from vault_backtest_writer import write_backtest_prediction
from vault_black_swan_writer import write_black_swan_event


def execute_snapshot(market: str, text: str) -> bool:
    return write_snapshot(market, text)


def execute_event(event_type: str, payload: dict) -> bool:
    return write_event(event_type, payload)


def execute_backtest(market: str, symbol: str, prediction: dict) -> bool:
    return write_backtest_prediction(market, symbol, prediction)


def execute_black_swan(event: dict) -> bool:
    return write_black_swan_event(event)
