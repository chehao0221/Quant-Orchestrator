import os
import sys
import json
from pathlib import Path

# ==================================================
# 路徑（⚠️ 以 GitHub Actions cwd 為準，這是關鍵）
# ==================================================
REPO_ROOT = Path.cwd()
BASE_DIR = REPO_ROOT / "repos" / "Quant-Guardian-Ultra"
SHARED_DIR = REPO_ROOT / "shared"
STATE_FILE = SHARED_DIR / "guardian_state.json"

# ==================================================
# 修正 modules 尾巴空白
# ==================================================
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
print("[DEBUG] cwd =", REPO_ROOT)
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# ==================================================
# imports
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

    SHARED_DIR.mkdir(parents=True, exist_ok=True)

    try:
        data_manager = DataManager()

        print("[PHASE] VIX 恐慌指數掃描")
        vix = VixScanner().scan()
        print(f"[INFO] VIX 指數：{vix}")

        print("[PHASE] 新聞掃描 / 去重")
        news = NewsScanner(data_manager).scan()
        print(f"[INFO] 新聞事件數：{len(news)}")

        print("[PHASE] 市場分析（台 / 美）")
        for market in ("TW", "US"):
            try:
                MarketAnalyst(market).analyze("INDEX")
            except Exception as e:
                print(f"[WARN] {market} 市場分析失敗：{e}")

        print("[PHASE] 風控評估")
        decision = DefenseManager().evaluate(vix, news)
        print("[RESULT] Guardian 判定結果：", decision)

        allow = decision.get("level") in ("L1", "L2")

    except Exception as e:
        print("[ERROR] Guardian 發生例外，保守停盤：", e)
        decision = {
            "level": "L4",
            "action": "HALT",
            "reason": str(e)
        }
        allow = False

    state = {
        "allow_trading": allow,
        "risk_level": decision.get("level"),
        "action": decision.get("action"),
        "reason": decision.get("reason", "")
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"[GUARDIAN] 已寫入 {STATE_FILE}")

    if not allow:
        notifier.trading_halt(
            level=state["risk_level"],
            reason="Guardian 判定風險偏高，今日停盤"
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


if __name__ == "__main__":
    main()
