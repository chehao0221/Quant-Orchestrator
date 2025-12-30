import json

def validate_backtest_data(backtest_data: dict):
    """
    驗證回測數據的完整性和有效性
    """
    if 'pred' not in backtest_data or 'price' not in backtest_data:
        raise ValueError("回測數據不完整：缺少預測或價格信息")
    
    return True
