import sys
import os
import json
from pathlib import Path
from datetime import datetime

# =====================================================
# Step 0：修正 modules 下「錯誤的資料夾名稱（尾隨空白）」
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"

def fix_folder(name: str):
    bad = MODULES_DIR / f"{name} "
    good = MODULES_DIR / name
    if bad.exists() and not good.exists():
        bad.rename(good)
        print(f"[FIX] rename '{name} ' -> '{name}'")

if MODULES_DIR.exists():
    for folder in ["scanners", "guardians", "analysts"]:
        fix_folder(folder)

# =====================================================
# Step 1：sys.path 保證正確
# =====================================================
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

print("[DEBUG] cwd =", os.getcwd())
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# =====================================================
# Step 2：安全 import（此時一定成功）
# =====================================================
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

from modules.scanners.vix_scanner import VixScanner
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseManager
from modules.analysts.market_analyst import MarketAnalyst

# =====================================================
# Step 3：Guardian 主流程
# =====================================================
def main():
    print("[GUARDIAN] 啟動 Guardian Ultra 盤後風控流程")

    notifier = DiscordNotifier()

    # 心跳（不中斷）
    try:
        notifier.heartbeat(mode="風險監控待命")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    # Data manager
    data_manager = DataManager()

    # ---------- VIX ----------
    print("[PHASE] VIX 恐慌指數掃描")
    vix = VixScanner().scan()
    print(f"[INFO] VIX 指數：{vix}")

    # ---------- News ----------
    print("[PHASE] 新聞掃描 / 去重")
    news = NewsScanner(data_manager).scan()
    print(f"[INFO] 新聞事件數：{len(news)}")

    # ---------- Market ----------
    print("[PHASE] 市場分析（台 / 美）")
    for market in ["TW", "US"]:
        try:
            MarketAnalyst(market).analyze()
        except Exception as e:
            print(f"[WARN] {market} 分析失敗：{e}")

    # ---------- Defense ----------
    print("[PHASE] 風控評估")
    defense = DefenseManager()
    decision = defense.evaluate(vix, news)

    print("[RESULT] Guardian 判定結果：", decision)

    level = decision.get("level", "L1")
    action = decision.get("action", "NORMAL")

    # ---------- Write shared state ----------
    shared_dir = BASE_DIR.parent.parent / "shared"
    shared_dir.mkdir(exist_ok=True)

    state_path = shared_dir / "guardian_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "action": action,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"[GUARDIAN] 已寫入 {state_path}")

    # ---------- Notify ----------
    if level == "L3":
        notifier.risk_warning(
            level="L3",
            summary="市場波動升高，建議降低短線曝險並提高警覺。",
        )
    elif level not in ["L1", "L2"]:
        notifier.trading_halt(
            reason="市場出現極端風險訊號，Guardian 已啟動防禦模式。"
        )

    print("[GUARDIAN] 本次盤後風控流程完成")


# =====================================================
# Entrypoint
# =====================================================
if __name__ == "__main__":
    main()
