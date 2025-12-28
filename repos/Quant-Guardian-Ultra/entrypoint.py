#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# ========= 基礎路徑處理 =========
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 修正 clone 時資料夾尾巴有空白的問題
modules_dir = BASE_DIR / "modules"
if modules_dir.exists():
    for p in modules_dir.iterdir():
        if p.name.endswith(" "):
            fixed = modules_dir / p.name.strip()
            if not fixed.exists():
                p.rename(fixed)
                print(f"[FIX] rename '{p.name}' -> '{fixed.name}'")

print(f"[DEBUG] cwd = {os.getcwd()}")
print(f"[DEBUG] modules contents = {[p.name for p in (BASE_DIR / 'modules').iterdir()]}")

# ========= 匯入核心元件 =========
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst


def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier(debug=True)

    # ========= 狀態管理 =========
    shared_state = BASE_DIR.parent.parent / "shared" / "guardian_state.json"
    shared_state.parent.mkdir(parents=True, exist_ok=True)

    data_manager = DataManager()

    # ========= Phase 1：VIX =========
    print("[PHASE] VIX 恐慌指數掃描")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    # ========= Phase 2：新聞 =========
    print("[PHASE] 新聞掃描 / 去重")
    news_scanner = NewsScanner(data_manager)
    news_events = news_scanner.scan()
    print(f"[INFO] 新聞事件數：{len(news_events)}")

    # ========= Phase 3：市場分析 =========
    print("[PHASE] 市場分析（台 / 美）")
    analyst_tw = MarketAnalyst("TW")
    analyst_us = MarketAnalyst("US")

    try:
        analyst_tw.analyze("MARKET")
    except Exception as e:
        print(f"[WARN] TW 市場分析失敗：{e}")

    try:
        analyst_us.analyze("MARKET")
    except Exception as e:
        print(f"[WARN] US 市場分析失敗：{e}")

    # ========= Phase 4：風控判定 =========
    print("[PHASE] 風控評估")
    defense = DefenseManager()

    decision = defense.evaluate(vix_value, news_events)
    print(f"[RESULT] Guardian 判定結果： {decision}")

    level = decision.get("level", "L1")
    action = decision.get("action", "NORMAL")

    # ========= 寫入 guardian_state.json =========
    state_payload = {
        "level": level,
        "action": action,
    }

    import json
    with open(shared_state, "w", encoding="utf-8") as f:
        json.dump(state_payload, f, ensure_ascii=False, indent=2)

    print(f"[GUARDIAN] 已寫入 {shared_state}")

    # ========= Discord 通知（只在 L3+） =========
    if level == "L3":
        notifier.guardian_l3(
            f"""市場狀態：風險升溫
風險等級：L3
建議動作：降低曝險（REDUCE）

摘要：
- VIX 偏高
- 偵測到市場不安新聞
- 尚未進入極端狀態

⚠️ 今日仍可觀察，但需保守應對"""
        )

    elif level in ("L4", "L5"):
        notifier.guardian_l4(
            f"""市場狀態：高風險
風險等級：{level}
系統動作：全面停盤

已觸發：
- Stock Genius：暫停
- Explorer：暫停
- 所有 AI 預測輸出：停止

⚠️ 請等待 Guardian 恢復"""
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


if __name__ == "__main__":
    main()
