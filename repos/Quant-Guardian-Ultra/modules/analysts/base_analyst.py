import yfinance as yf
import pandas as pd
import os
from xgboost import XGBRegressor

class BaseAnalyst:
    def __init__(self, market_name):
        self.market_name = market_name
        self.model_path = f"data/models/{market_name}_model.xgb"
        os.makedirs("data/models", exist_ok=True)

    def calculate_indicators(self, df):
        df = df.copy()
        df["ret"] = df["Close"].pct_change()
        df["ma20_gap"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
        df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()
        df["target"] = df["Close"].shift(-5) / df["Close"] - 1
        return df.dropna()

    def load_or_train(self, df, feats):
        model = XGBRegressor(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05
        )

        if os.path.exists(self.model_path):
            model.load_model(self.model_path)
            return model

        train = df.iloc[:-5]
        model.fit(train[feats], train["target"])
        model.save_model(self.model_path)
        return model

    def predict(self, symbol):
        try:
            data = yf.download(symbol, period="2y", progress=False)
            if len(data) < 60:
                return None

            df = self.calculate_indicators(data)
            feats = ["ret", "ma20_gap", "vol_ratio"]

            model = self.load_or_train(df, feats)
            pred = float(model.predict(df[feats].iloc[-1:])[0])

            return {
                "symbol": symbol,
                "price": round(float(data["Close"].iloc[-1]), 2),
                "pred": pred
            }
        except:
            return None
