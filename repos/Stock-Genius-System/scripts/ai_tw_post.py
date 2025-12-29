from datetime import datetime
from utils import load_top5, load_core_watch, load_backtest
from notifier import send_discord

def confidence_emoji(conf):
    if conf >= 60:
        return "🟢"
    elif conf >= 40:
        return "🟡"
    else:
        return "🔴"

def render_stock_line(code, pred, conf, price, sup, res):
    emoji = confidence_emoji(conf)
    return (
        f"{emoji} {code}：預估 {pred:+.2f}%   信心度 {conf}%\n"
        f"└ 現價 {price}（支撐 {sup} / 壓力 {res}）"
    )

def main():
    today = datetime.today().strftime("%Y-%m-%d")

    top5 = load_top5("TW")
    core = load_core_watch("TW")
    backtest = load_backtest("TW")

    lines = []
    lines.append(f"📊 台股 AI 進階預測報告 ({today})")
    lines.append("------------------------------------------\n")
    lines.append("🔍 AI 海選 Top 5（潛力股）")

    for s in top5:
        lines.append(render_stock_line(**s))

    lines.append("\n👁 台股核心監控（固定顯示）")
    for s in core:
        lines.append(render_stock_line(**s))

    lines.append("\n------------------------------------------")
    lines.append("📊 台股｜近 5 日回測結算（歷史觀測）\n")
    lines.append(f"交易筆數：{backtest['trades']}")
    lines.append(f"命中率：{backtest['hit_rate']}%")
    lines.append(f"平均報酬：{backtest['avg_return']}%")
    lines.append(f"最大回撤：{backtest['max_dd']}%\n")
    lines.append("📌 本結算僅為歷史統計觀測，不影響任何即時預測或系統行為\n")
    lines.append("💡 模型為機率推估，僅供研究參考，非投資建議。")

    send_discord("\n".join(lines), market="TW")

if __name__ == "__main__":
    main()
