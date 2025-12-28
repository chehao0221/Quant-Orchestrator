#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# ========= 基本路徑 =========
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
SHARED_DIR = REPO_ROOT / "shared"
STATE_FILE = SHARED_DIR / "guardian_state.json"

# ========= sys.path =========
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "core"))
sys.path.insert(0, str(BASE_DIR / "modules"))

print(f"[DEBUG] cwd = {os.getcwd()}")

# ========= 修正錯誤資料夾名稱 =========
modules_dir = BASE_DIR / "modules"
for bad in ["scanners ", "guardians "]:
    bad_path = modules_dir / bad
    if bad_path.exists():
        bad_path.rename(modules_dir / bad.strip())
        print(f"[FIX] rename '{bad}' -> '{bad.strip()}'")

print(f"[DEBUG] modules contents = {os.listdir(modules_dir)}")

# ========= 匯入模組（完全對齊原設計） =========
from core.data_manager import DataManager
from core.notifier import DiscordNotifier

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst


# ========= Guardian 狀態寫入 =========
def write_guardian_state(result: dict):
    SHARED_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds"),
        "level": result.get("level"),
        "action": result.get("action"),
        "source": "Quant-Guardian-Ultra",
    }

    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    if not STATE_FILE.exists():
        raise RuntimeError("guardian_state.json 寫入失敗")

    print(f"[GUARDIAN] 已寫入 {STATE_FILE}")


# ========= 主流程 =========
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()

    # ---------- DataManager（⚠️ 關鍵） ----------
    data_manager = DataManager()

    # ---------- Phase 1：VIX ----------
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # ---------- Phase 2：新聞 ----------
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # ---------- Phase 3：市場分析 ----------
    print("[PHASE] 市場分析（台 / 美）")
    try:
        MarketAnalyst("TW").analyze()
    except Exception as e:
        print(f"[WARN] TW 市場分析失敗：{e}")

    try:
        MarketAnalyst("US").analyze()
    except Exception as e:
        print(f"[WARN] US 市場分析失敗：{e}")

    # ---------- Phase 4：風控評估 ----------
    print("[PHASE] 風控評估")
    defense = DefenseManager()
    decision = defense.evaluate(vix_value, news_events)

    print(f"[RESULT] Guardian 判定結果： {decision}")

    # ---------- Phase 5：寫入共享狀態 ----------
    write_guardian_state(decision)

    # ---------- Phase 6：通知 ----------
    level = decision.get("level")

    color_map = {
        "L1": "綠",
        "L2": "綠",
        "L3": "黃",
        "L4": "紅",
        "L5": "紅",
        "L6": "紅",
    }

    color = color_map.get(level, "黃")

    if level == "L3":
        notifier.send(
            kind="general",
            title="⚠️ Guardian 風險提醒",
            message=(
                f"風險等級：{level}\n"
                f"系統狀態：風險升高（已降速）\n\n"
                f"建議：注意市場波動"
            ),
            color=color,
        )

    if level in ("L4", "L5", "L6"):
        notifier.send(
            kind="black_swan",
            title="🛑 Guardian 判定今日停盤",
            message=(
                f"風險等級：{level}\n"
                f"系統狀態：全面防禦\n\n"
                f"Stock-Genius / Explorer 已進入暫停狀態"
            ),
            color="紅",
        )


    print("[GUARDIAN] 本次盤後風控流程完成")


# ========= 入口 =========
if __name__ == "__main__":
    main()
