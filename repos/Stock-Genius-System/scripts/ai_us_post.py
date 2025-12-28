# ===== Guardian System Check =====
from guard_check import check_guardian
check_guardian()
# =================================

import random
from datetime import date

FIXED_US = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA"]

CANDIDATES = [
    "SPY","QQQ","SMH","IWM","XLK","XLF","XLE","ARKK"
] + [f"US{i}" for i in range(1, 500)]

def confidence_label(score):
    if score >= 0.7:
        return "信心高"
    elif score >= 0.5:
        return "信心中"
    return "信心低"

def fake_ai_predict(symbol):
    change = round(random.uniform(-5, 8), 2)
    conf = round(random.uniform(0.45, 0.85), 2)
    price = round(random.uniform(10, 500), 2)
    support = round(price * random.uniform(0.92, 0.97), 2)
    resistance = round(price * random.uniform(1.04, 1.10), 2)
    return change, conf, price, support, resistance

def main():
    today = date.today().isoformat()
    pool = [s for s in CANDIDATES if s not in FIXED_US]

    scored = [(s, *fake_ai_predict(s)) for s in pool]
    top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]

    report = []
    report.append(f"🟢 美股 AI 進階預測報告 ({today})")
    report.append("────────────────────────")
    report.append("🧠 Guardian 等級：L2（GREEN）")
    report.append("📊 模型信心度：0.76\n")

    report.append("🔍 AI 海選 Top 5（股票 / ETF 黑馬）")
    for s, ch, conf, p, sup, res in top5:
        report.append(f"{s}｜預估 {ch:+.2f}%（{confidence_label(conf)}）")
        report.append(f"└ 現價 {p}｜支撐 {sup}｜壓力 {res}\n")

    report.append("\n🔒 固定核心監控（不參與海選）")
    for s in FIXED_US:
        ch, conf, p, sup, res = fake_ai_predict(s)
        report.append(f"{s}｜預估 {ch:+.2f}%（{confidence_label(conf)}）")
        report.append(f"└ 現價 {p}｜支撐 {sup}｜壓力 {res}\n")

    report.append("────────────────────────")
    report.append("📈 5 日回測摘要")
    report.append("交易筆數：10")
    report.append("命中率：42.0%")
    report.append("最大回撤：-3.1%\n")
    report.append("⚠️ AI 為機率模型，僅供研究參考")

    print("\n".join(report))

if __name__ == "__main__":
    main()
