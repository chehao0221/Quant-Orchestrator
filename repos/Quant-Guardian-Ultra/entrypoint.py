import os
import sys
import json
from pathlib import Path

# ==================================================
# 🔥 修正 modules 下尾巴有空白的資料夾（只做一次）
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
# 🔧 sys.path（repo root）
# ==================================================
sys.path.insert(0, str(BASE_DIR))

print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# ==================================================
# ✅ imports（完全對齊你原始設計）
# ==================================================
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst

# ==================================================
# 🧠 Guardian 主流程
# ==================================================
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()
    notifier.heartbeat(mode="風險監控待命")

    # ---------- Phase 0：Data Manager ----------
    data_path = BASE_DIR / "data" / "state.json"
    data_manager = DataManager(data_path=str(data_path))

    # ---------- Phase 1：VIX ----------
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # ---------- Phase 2：新聞 ----------
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager=data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # ---------- Phase 3：市場分析 ----------
    print("[PHASE] 市場分析（台 / 美）")

    tw_analyst = MarketAnalyst(market="TW")
    us_analyst = MarketAnalyst(market="US")

    tw_result = tw_analyst.analyze()
    us_result = us_analyst.analyze()

    # ---------- Phase 4：風控判斷 ----------
    print("[PHASE] 風控評估")

    defense = DefenseManager()
    decision = defense.evaluate(
        vix=vix_value,
        news=news_events,
        tw=tw_result,
        us=us_result,
    )

    print("[RESULT] Guardian 判定結果：", decision)

    # ---------- Phase 5：寫入共享狀態 ----------
    shared_state = {
        "allow_trading": decision.get("level") in ("L1", "L2"),
        "risk_level": decision.get("level"),
        "action": decision.get("action"),
    }

    shared_path = BASE_DIR.parent.parent / "shared" / "guardian_state.json"
    shared_path.parent.mkdir(parents=True, exist_ok=True)

    with open(shared_path, "w", encoding="utf-8") as f:
        json.dump(shared_state, f, ensure_ascii=False, indent=2)

    # ---------- Phase 6：通知 ----------
    if not shared_state["allow_trading"]:
        notifier.trading_halt(
            level=shared_state["risk_level"],
            reason="市場風險過高（VIX / 新聞 / 市場分析）",
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


if __name__ == "__main__":
    main()
