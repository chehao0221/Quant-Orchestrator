import os
import sys
from pathlib import Path
from datetime import datetime

# =====================================================
# Phase 0 — 修正 modules 底下「尾端空白資料夾」
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"

if MODULES_DIR.exists():
    for item in MODULES_DIR.iterdir():
        if item.is_dir() and item.name.endswith(" "):
            fixed = item.with_name(item.name.rstrip())
            if not fixed.exists():
                item.rename(fixed)
                print(f"[FIX] rename '{item.name}' -> '{fixed.name}'")

# =====================================================
# Phase 1 — sys.path 設定
# =====================================================

sys.path.insert(0, str(BASE_DIR))

print("[DEBUG] sys.path =", sys.path)
print(
    "[DEBUG] modules contents =",
    [p.name for p in (BASE_DIR / "modules").iterdir() if p.is_dir()],
)

# =====================================================
# Phase 2 — Import（修完後一定可成功）
# =====================================================

from core.data_manager import DataManager
from core.notifier import Notifier

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner

from modules.analysts.market_analyst import MarketAnalyst
from modules.guardians.defense import DefenseManager


# =====================================================
# Phase 3 — Guardian 主流程（盤後一次性）
# =====================================================

def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    # --- 初始化核心 ---
    data_manager = DataManager()
    notifier = Notifier()

    # --- 系統心跳 ---
    try:
        notifier.send(
            f"🛡 Guardian 系統心跳回報\n\n"
            f"系統狀態：正常監控中\n"
            f"檢查時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"模式：盤後風控檢查",
            channel="general",
        )
    except Exception as e:
        print(f"[WARN] Discord Webhook 未設定（general）")

    # =================================================
    # Phase 3.1 — VIX Scanner
    # =================================================
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # =================================================
    # Phase 3.2 — News Scanner（含去重）
    # =================================================
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # =================================================
    # Phase 3.3 — 市場分析（台 / 美）
    # =================================================
    print("[PHASE] 市場分析（台 / 美）")
    analyst = MarketAnalyst()
    market_report = analyst.analyze()

    if market_report.get("tw"):
        notifier.send(
            market_report["tw"],
            channel="tw",
        )

    if market_report.get("us"):
        notifier.send(
            market_report["us"],
            channel="us",
        )

    # =================================================
    # Phase 3.4 — Defense Guardian（L1–L4）
    # =================================================
    print("[PHASE] 風險防禦評估")
    defense = DefenseManager()

    defense_result = defense.evaluate(
        vix=vix_value,
        news_events=news_events,
    )

    print("[RESULT] Defense 評估結果：", defense_result)

    level = defense_result.get("level", "L1")
    action = defense_result.get("action", "NONE")

    # --- 更新 state.json ---
    data_manager.update_risk_state(
        level=level,
        action=action,
        vix=vix_value,
    )

    # --- 依等級通知 ---
    if level in ["L3", "L4"]:
        notifier.send(
            f"🚨 黑天鵝風險警示\n\n"
            f"等級：{level}\n"
            f"動作：{action}\n"
            f"VIX：{vix_value}",
            channel="black_swan",
        )
    else:
        notifier.send(
            f"🛡 風控完成回報\n\n"
            f"等級：{level}\n"
            f"動作：{action}\n"
            f"VIX：{vix_value}",
            channel="general",
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


# =====================================================
# Entrypoint
# =====================================================

if __name__ == "__main__":
    main()
