import yfinance as yf
from datetime import datetime

class CounterfactualEngine:
    def run_simulation(self, symbols):
        results = []
        for s in symbols:
            try:
                data = yf.download(s, period="5d", progress=False)
                if data.empty: continue
                perf = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
                results.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "symbol": s, 
                    "sim_ret": round(float(perf), 4)
                })
            except: continue
        return results
