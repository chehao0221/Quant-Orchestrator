import sys
import os
import json
from pathlib import Path
from datetime import datetime

# =========================
# 路徑修正（防止 modules / core 找不到）
# =========================
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

MODULES_DIR = BASE_DIR / "modules"
if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

print("[DEBUG] cwd =", os.getcwd())
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# =========================
# 匯入核心元件
# =========================
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst


# =========================
# Guardian 主流程
# =========================
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()

    # 🫀 心跳（不影響流程）
    try:
        notifier.heartbeat(mode="風險監控待命")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    # =========================
    # 資料管理（state.json）
    # =========================
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    data_manager = DataManager()

    # =========================
    # Phase 1：VIX
    # =========================
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # =========================
    # Phase 2：新聞掃描
    # =========================
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # =========================
    # Phase 3：市場分析（只做觀測）
    # =========================
    print("[PHASE] 市場分析（台 / 美）")
    market_results = {}

    for market in ["TW", "US"]:
        try:
            analyst = MarketAnalyst(market)
            market_results[market] = analyst.analyze()
        except Exception as e:
            print(f"[WARN] {market} 市場分析失敗：{e}")
            market_results[market] = None

    # =========================
    # Phase 4：風控評估
    # =========================
    print("[PHASE] 風控評估")
    defense = DefenseManager()

    decision = defense.evaluate(
        vix_value,
        news_events,
    )

    print("[RESULT] Guardian 判定結果：", decision)

    level = decision.get("level", "L1")
    action = decision.get("action", "NORMAL")

    # =========================
    # 寫入 shared 狀態（給 Genius / Explorer 用）
    # =========================
    shared_dir = BASE_DIR.parent.parent / "shared"
    shared_dir.mkdir(exist_ok=True)

    guardian_state_path = shared_dir / "guardian_state.json"
    guardian_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "action": action,
    }

    with open(guardian_state_path, "w", encoding="utf-8") as f:
        json.dump(guardian_state, f, ensure_ascii=False, indent=2)

    print(f"[GUARDIAN] 已寫入 {guardian_state_path}")

    # =========================
    # Discord 通知策略
    # =========================
    if level in ["L1", "L2"]:
        # 🟢 靜默，不通知
        pass

    elif level == "L3":
        notifier.risk_warning(
            level="L3",
            summary="市場波動升高，建議降低短線曝險並提高警覺。"
        )

    else:
        # 🔴 L4 / L5 / L6
        notifier.trading_halt(
            reason="市場出現極端風險訊號，Guardian 已啟動全面防禦模式。"
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    main()
