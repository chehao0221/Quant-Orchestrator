import json
from pathlib import Path

def read_backtest_data(backtest_file: str):
    """
    讀取 Vault 儲存的回測數據
    """
    backtest_data = {}
    if Path(backtest_file).exists():
        with open(backtest_file, 'r') as f:
            backtest_data = json.load(f)
    return backtest_data
