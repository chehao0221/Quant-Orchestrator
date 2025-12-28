import hashlib
from datetime import datetime
import pytz

from core import GuardianEngine, Notifier
from modules.scanners.news import NewsScanner
from modules.scanners.vix_scanner import VixScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst

def main():
    engine = GuardianEngine()
    notifier = Notifier()

    tz = pytz.timezone("Asia/Taipei")
    now = datetime.now(tz)
    h = now.hour

    # --- 1️⃣ 風險掃描 ---
    news_lv, news_list = NewsScanner().scan()
    vix_lv = VixScanner().check_vix()
    defense_lv = DefenseManager().evaluate()

    risk_lv = max(news_lv, vix_lv, defense_lv)

    if news_list:
        content = "".join(news_list)
        news_hash = hashlib.md5(content.encode()).hexdigest()

        if engine.state.get("last_news_hash") != news_hash:
            if risk_lv >= 4:
                engine.set_risk(4, pause_hours=8)
                notifier.send(
                    "swan",
                    "🚨 黑天鵝風險警報",
                    news_list[0],
                    color=0xff0000
                )
            elif h in [8, 14, 20]:
                notifier.send(
                    "news",
                    "📰 市場焦點",
                    "\n".join(news_list[:5]),
                    color=0x95a5a6
                )

            engine.state["last_news_hash"] = news_hash
            engine.save_state()

    # --- 2️⃣ AI 分析 ---
    if not engine.is_paused():
        if h == 14:
            analyst = MarketAnalyst("TW")
            for s in ["2330.TW", "2317.TW", "2454.TW"]:
                res = analyst.analyze(s)
                if res:
                    notifier.send(
                        "tw",
                        f"📈 台股盤後：{s}",
                        f"收盤價：{res['price']}\n預測報酬：{res['pred']:.2%}",
                        color=0x2ecc71
                    )

        if h == 6:
            analyst = MarketAnalyst("US")
            for s in ["NVDA", "TSLA", "AAPL"]:
                res = analyst.analyze(s)
                if res:
                    notifier.send(
                        "us",
                        f"🇺🇸 美股盤後：{s}",
                        f"收盤價：{res['price']}\n預測報酬：{res['pred']:.2%}",
                        color=0x3498db
                    )

if __name__ == "__main__":
    main()
