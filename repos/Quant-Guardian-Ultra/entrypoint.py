import os
import sys

# =========================
# 基本路徑設定
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")

# =========================
# 🔥 自動修復：modules 底下尾端空白資料夾
# =========================
if os.path.isdir(MODULES_DIR):
    for name in os.listdir(MODULES_DIR):
        stripped = name.rstrip()
        if name != stripped:
            src = os.path.join(MODULES_DIR, name)
            dst = os.path.join(MODULES_DIR, stripped)
            if not os.path.exists(dst):
                print(f"[FIX] rename '{name}' -> '{stripped}'")
                os.rename(src, dst)

# =========================
# sys.path 保證
# =========================
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# =========================
# Core imports
# =========================
from core.engine import GuardianEngine
from core.data_manager import DataManager
from core.notifier import Notifier

# =========================
# Modules imports（名稱已對齊實際 class）
# =========================
from modules.scanners.news import NewsScanner
from modules.scanners.vix_scanner import VIXFearScanner   # ← 關鍵修正
from modules.guardians.defense import DefenseGuardian
from modules.analysts.market_analyst import MarketAnalyst


def main():
    engine = GuardianEngine(
        data_manager=DataManager(),
        notifier=Notifier(),
    )

    # Scanners
    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXFearScanner())

    # Guardians
    engine.register_guardian(DefenseGuardian())

    # Analysts
    engine.register_analyst(MarketAnalyst())

    engine.run()


if __name__ == "__main__":
    main()
