import os
import xgboost as xgb

class QuantModel:
    def __init__(self, name):
        self.path = f"data/models/{name}.xgb"
        os.makedirs("data/models", exist_ok=True)
        self.model = xgb.XGBRegressor()

    def save(self):
        self.model.save_model(self.path)

    def load(self):
        if os.path.exists(self.path):
            self.model.load_model(self.path)
            return True
        return False
