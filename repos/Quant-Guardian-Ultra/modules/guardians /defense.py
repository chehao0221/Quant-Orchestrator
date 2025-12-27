import yfinance as yf

class DefenseManager:
    def evaluate(self):
        """
        根據避險資產表現，回傳建議風險等級
        """
        try:
            assets = ["GLD", "BIL", "VIXY"]
            data = yf.download(assets, period="5d", progress=False)["Close"]

            if data.empty:
                return 1

            rets = (data.iloc[-1] / data.iloc[0]) - 1

            # 避險資產大漲 → 市場異常
            if rets.get("VIXY", 0) > 0.15:
                return 4
            if rets.mean() > 0.05:
                return 3

            return 1
        except:
            return 1
