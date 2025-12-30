# AI 自我學習閉環（不可直接被預測呼叫）

from performance_judge_ai import judge
from weight_optimizer_ai import optimize
import json
import os

WEIGHT_PATH = "LOCKED_DECISION/horizon/ai_weights.json"

def load_weights():
    with open(WEIGHT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_weights(w):
    with open(WEIGHT_PATH, "w", encoding="utf-8") as f:
        json.dump(w, f, indent=2)

def learning_step(backtest_result: dict):
    weights = load_weights()
    score = judge(backtest_result)["score"]
    new_weights = optimize(weights, score)
    save_weights(new_weights)
