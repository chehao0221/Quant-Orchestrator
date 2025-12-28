from core.engine import GuardianEngine
import random

def get_risk_signals():
    """
    風控訊號產生器
    未來可替換成：
    - 真實 VIX
    - 新聞情緒模型
    - 黑天鵝偵測模型
    """
    vix = random.uniform(15, 40)          # 模擬市場波動
    sentiment = random.uniform(-1, 1)     # 模擬情緒
    event_score = random.uniform(0, 1)    # 模擬極端事件機率
    return vix, sentiment, event_score

def main():
    engine = GuardianEngine()

    vix, sentiment, event_score = get_risk_signals()

    decision = engine.run(
        vix=vix,
        sentiment=sentiment,
        event_score=event_score
    )

    print(
        f"[Guardian] Level=L{decision.level} | "
        f"Freeze={decision.freeze} | "
        f"{decision.description}"
    )

if __name__ == "__main__":
    main()
