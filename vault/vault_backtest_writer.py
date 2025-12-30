import json
from pathlib import Path

def write_backtest_data(backtest_file: str, data: dict):
    """
    將回測數據寫入 Vault
    """
    with open(backtest_file, 'w') as f:
        json.dump(data, f, indent=4)
