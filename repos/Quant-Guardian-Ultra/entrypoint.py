#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# ========= 基本路徑設定 =========
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent  # Quant-Orchestrator/
SHARED_DIR = REPO_ROOT / "shared"
STATE_FILE = SHARED_DIR / "guardian_state.json"

# 動態加入模組路徑
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "core"))
sys.path.insert(0, str(BASE_DIR / "modules"))

print(f"[DEBUG] cwd = {os.getcwd()}")

# ========= 修正錯誤資料夾名稱（scanners / guardians） =========
modules_dir = BASE_DIR / "modules"
for bad in ["scanners ", "guardians "]:
    bad_path = modules_dir / bad
    if bad_path.exists():
        fixed = bad.strip()
        bad_path.rename(modules_dir / fixed)
        print(f"[FIX] rename '{bad}' -> '{fixed}'")

print(f"[DEBUG] modules contents = {os.listdir(modules_dir)}")

# ========= 匯入系統元件 =========
from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst
from core.notifier import DiscordNotifier


# ========= 寫入 Guardian 狀態（關鍵修正） =========
def write_guardian_state(result: dict):
    """
    一定會寫入 shared/guardian_state.json
    失敗就直接 raise，不吞錯
    """
    SHARED_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds"),
        "level": result.get("level"),
        "action": result.get("action"),
        "source": "Quant-Guardian-Ultra",
    }

    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # 實際驗證檔案存在
    if not STATE_FILE.exists():
        raise RuntimeError("guardian_state.json 寫入失敗（檔案不存在）")

    print(f"[GUARDIAN] 已寫入 {STATE_FILE}")


# ========= 主流程 =========
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()

    # ---------- Phase 1：VIX ----------
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # ---------- Phase 2：新聞 ----------
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner()
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

    # ---------- Phase 5：寫入共享狀態（最重要） ----------
    write_guardian_state(decision)

    # ---------- Phase 6：通知（依等級） ----------
    level = decision.get("level")

    # 顏色規則：綠 / 黃 / 紅
    color_map = {
        "L1": "綠",
        "L2": "綠",
        "L3": "黃",
        "L4": "紅",
        "L5": "紅",
        "L6": "紅",
    }

    color = color_map.get(level, "黃")

    if level in ("L3",):
        notifier.general(
            title="⚠️ Guardian 風險提醒",
            message=f"風險等級：{level}\n狀態：{decision['action']}",
            color=color,
        )

    if level in ("L4", "L5", "L6"):
        notifier.black_swan(
            title="🛑 Guardian 判定今日停盤",
            message=f"風險等級：{level}\n系統已進入防禦狀態",
            color="紅",
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


# ========= 入口 =========
if __name__ == "__main__":
    main()
