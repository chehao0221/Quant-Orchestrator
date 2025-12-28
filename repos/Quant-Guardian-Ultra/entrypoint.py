import os
import sys
import json
from pathlib import Path

# ==================================================
# 修正 modules 資料夾尾巴空白
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"

if MODULES_DIR.exists():
    for p in MODULES_DIR.iterdir():
        if p.is_dir() and p.name.endswith(" "):
            fixed = MODULES_DIR / p.name.rstrip()
            if not fixed.exists():
                print(f"[FIX] rename '{p.name}' -> '{fixed.name}'")
                p.rename(fixed)

# ==================================================
# sys.path
# ==================================================
sys.path.insert(0, str(BASE_DIR))
print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# ==================================================
# imports（嚴格對齊原始模組）
# ==================================================
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst

# ==================================================
# Guardian 主流程
# ==================================================
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()
    notifier.heartbeat(mode="風險監控待命")

    # ---------- Data Manager ----------
    data_manager = DataManager()

    # ---------- VIX ----------
    print("[PHASE] VIX 恐慌指數掃描")
    vix_value = VixScanner().scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # ---------- News ----------
    print("[PHASE] 新聞掃描 / 去重")
    news_events = NewsScanner(data_manager).scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # ---------- Market Analyst（存在性檢查，不誤用） ----------
    print("[PHASE] 市場分析（台 / 美）")

    def check_market_analyst(market: str):
        try:
            MarketAnalyst(market)
            return "AVAILABLE"
        except Exception as e:
            print(f"[WARN] {market} 市場分析模組不可用：{e}")
            return "UNAVAILABLE"

    tw_status = check_market_analyst("TW")
    us_status = check_market_analyst("US")

    # ---------- Defense ----------
    print("[PHASE] 風控評估")
    defense = DefenseManager()

    # ⚠️ 嚴格使用位置參數（不破壞原始設計）
    decision = defense.evaluate(
        vix_value,
        tw_status,
        us_status,
    )

    print("[RESULT] Guardian 判定結果：", decision)

    # ---------- 輸出共享狀態（只做控制，不交易） ----------
    shared_state = {
        "allow_trading": decision.get("level") in ("L1", "L2"),
        "risk_level": decision.get("level"),
        "action": decision.get("action"),
        "reason": decision.get("reason", ""),
    }

    shared_path = BASE_DIR.parent.parent / "shared" / "guardian_state.json"
    shared_path.parent.mkdir(parents=True, exist_ok=True)

    with open(shared_path, "w", encoding="utf-8") as f:
        json.dump(shared_state, f, ensure_ascii=False, indent=2)

    # ---------- 通知 ----------
    if not shared_state["allow_trading"]:
        notifier.trading_halt(
            level=shared_state["risk_level"],
            reason="Guardian 判定風險偏高，系統暫停交易",
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


if __name__ == "__main__":
    main()
