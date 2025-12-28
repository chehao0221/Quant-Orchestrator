import os
import sys
import json
from pathlib import Path
from datetime import datetime

# =====================================================
# Phase 0 — 修正 modules 尾端空白資料夾
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
# Phase 1 — sys.path
# =====================================================

sys.path.insert(0, str(BASE_DIR))

print("[DEBUG] modules contents =",
      [p.name for p in (BASE_DIR / "modules").iterdir() if p.is_dir()])

# =====================================================
# Imports
# =====================================================

from core.data_manager import DataManager
from core.notifier import Notifier

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst

# =====================================================
# Guardian 主流程
# =====================================================

def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    data_manager = DataManager()
    notifier = Notifier()

    # -------------------------------
    # 系統心跳
    # -------------------------------
    notifier.send(
        f"🛡 Guardian 系統心跳回報\n\n"
        f"系統狀態：正常監控中\n"
        f"檢查時間：{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"模式：盤後風控檢查",
        channel="general",
    )

    # -------------------------------
    # VIX Scanner
    # -------------------------------
    print("[PHASE] VIX 恐慌指數掃描")
    vix = VixScanner().scan()
    print(f"[INFO] VIX 指數：{vix}")

    # -------------------------------
    # News Scanner
    # -------------------------------
    print("[PHASE] 新聞掃描 / 去重")
    news_events = NewsScanner(data_manager).scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # -------------------------------
    # 市場分析（⚠️ 必須防炸）
    # -------------------------------
    print("[PHASE] 市場分析（台 / 美）")

    try:
        tw_report = MarketAnalyst(market="tw").analyze()
        if tw_report:
            notifier.send(tw_report, channel="tw")
    except Exception as e:
        print(f"[WARN] 台股分析失敗：{e}")

    try:
        us_report = MarketAnalyst(market="us").analyze()
        if us_report:
            notifier.send(us_report, channel="us")
    except Exception as e:
        print(f"[WARN] 美股分析失敗：{e}")

    # -------------------------------
    # Defense Guardian（核心不可中斷）
    # -------------------------------
    print("[PHASE] 風險防禦評估")
    defense = DefenseManager()
    result = defense.evaluate(vix=vix, news_events=news_events)

    level = result["level"]
    action = result["action"]

    print("[RESULT]", result)

    # -------------------------------
    # Guardian → shared 狀態（交易開關）
    # -------------------------------
    shared_dir = BASE_DIR.parents[1] / "shared"
    shared_dir.mkdir(exist_ok=True)
    guardian_state = shared_dir / "guardian_state.json"

    allow_trading = level in ["L1", "L2"]

    with open(guardian_state, "w", encoding="utf-8") as f:
        json.dump(
            {
                "allow_trading": allow_trading,
                "risk_level": level,
                "action": action,
                "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    # -------------------------------
    # 通知
    # -------------------------------
    if level in ["L3", "L4"]:
        notifier.send(
            f"🚨 黑天鵝風險警示\n\n"
            f"等級：{level}\n"
            f"動作：{action}\n"
            f"VIX：{vix}",
            channel="black_swan",
        )
    else:
        notifier.send(
            f"🛡 風控完成\n等級：{level}\nVIX：{vix}",
            channel="general",
        )

    print("[GUARDIAN] 盤後風控流程完成")


if __name__ == "__main__":
    main()
