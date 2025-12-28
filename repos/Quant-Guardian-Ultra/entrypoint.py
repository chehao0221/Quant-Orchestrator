import os
import sys
import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 保證 Guardian repo root 在 sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# === 🔥 強制註冊 modules 為 Python module（不依賴 __init__.py） ===
MODULES_DIR = os.path.join(BASE_DIR, "modules")

if os.path.isdir(MODULES_DIR):
    modules_pkg = types.ModuleType("modules")
    modules_pkg.__path__ = [MODULES_DIR]
    sys.modules["modules"] = modules_pkg

# === Debug ===
print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules dir exists =", os.path.isdir(MODULES_DIR))
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# === Core ===
from core.engine import GuardianEngine
from core.data_manager import DataManager
from core.notifier import Notifier

# === Modules（現在 100% 不會再炸） ===
from modules.scanners.news import NewsScanner
from modules.scanners.vix_scanner import VIXScanner
from modules.guardians.defense import DefenseGuardian
from modules.analysts.market_analyst import MarketAnalyst


def main():
    engine = GuardianEngine(
        data_manager=DataManager(),
        notifier=Notifier(),
    )

    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScanner())
    engine.register_guardian(DefenseGuardian())
    engine.register_analyst(MarketAnalyst())

    engine.run()


if __name__ == "__main__":
    main()
