from .base_analyst import BaseAnalyst

class MarketAnalyst(BaseAnalyst):
    def __init__(self, market):
        super().__init__(market)

    def analyze(self, symbol):
        # 直接調用 base_analyst.py 裡的 predict 邏輯
        return self.predict(symbol)
