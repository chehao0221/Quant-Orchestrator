# repos/Quant-Guardian-Ultra/entrypoint.py
import sys
import os
from pathlib import Path

# === Path 修正（防 modules / core 找不到） ===
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# === 修正資料夾名稱有空白的問題（scanners / guardians） ===
modules_dir = BASE_DIR / "modules"
if modules_dir.exists():
    for name in os.listdir(modules_dir):
        if name.endswith(" "):
            fixed = name.rstrip()
            os.rename(modules_dir / name, modules_dir / fixed)
            print(f"[FIX] rename '{name}' -> '{fixed}'")

# === Imports ===
from core.notifier import DiscordNotifier
from core.data_manager import DataManager
from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst


def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    # === Notifier ===
    notifier = DiscordNotifier(
        general=os.getenv("DISCORD_WEBHOOK_GENERAL"),
        black_swan=os.getenv("DISCORD_WEBHOOK_BLACK_SWAN"),
        us=os.getenv("DISCORD_WEBHOOK_US"),
        tw=os.getenv("DISCORD_WEBHOOK_TW"),
    )

    # === Data Manager ===
    shared_state = Path(__file__).resolve().parents[2] / "shared" / "guardian_state.json"
    shared_state.parent.mkdir(parents=True, exist_ok=True)
    data_manager = DataManager()

    # === Heartbeat（失敗不影響流程） ===
    notifier.heartbeat(mode="風險監控待命")

    # === Phase 1: VIX ===
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # === Phase 2: News ===
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # === Phase 3: Market Analysis（台 / 美）===
    print("[PHASE] 市場分析（台 / 美）")
    market_results = {}

    for market in ("tw", "us"):
        try:
            analyst = MarketAnalyst(market)
            market_results[market] = analyst.analyze(symbol=None)
        except Exception as e:
            print(f"[WARN] {market.upper()} 市場分析失敗：{e}")
            market_results[market] = None

    # === Phase 4: Defense ===
    print("[PHASE] 風控評估")
    defense = DefenseManager()
    decision = defense.evaluate(vix_value, news_events)
    print(f"[RESULT] Guardian 判定結果： {decision}")

    # === Write state ===
    state = {
        "level": decision["level"],
        "action": decision["action"],
    }
    shared_state.write_text(
        __import__("json").dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[GUARDIAN] 已寫入 {shared_state}")

    level = decision["level"]

    # === 行為分流（⚠️ 關鍵：L3 必須 return） ===
    if level in ("L1", "L2"):
        print("[GUARDIAN] 低風險（綠），不通知")
        return

    if level == "L3":
        notifier.risk_alert(
            level="L3",
            title="🟡 市場風險升高",
            message="目前市場波動升高，建議降低曝險，系統持續監控中。",
        )
        print("[GUARDIAN] L3 處理完成（一般提醒）")
        return

    # === L4+ Black Swan ===
    notifier.trading_halt(
        level=level,
        title="🔴 黑天鵝警報｜今日停盤",
        message="系統偵測到極端風險，已建議全面停盤並暫停所有下游流程。",
    )

    print("[GUARDIAN] 黑天鵝流程完成")


if __name__ == "__main__":
    main()
