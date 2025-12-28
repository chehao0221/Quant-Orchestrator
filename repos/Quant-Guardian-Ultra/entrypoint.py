import os
import sys
import importlib
import inspect

# =========================
# 基本路徑
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")

# =========================
# 🔥 修復 modules 底下尾端空白資料夾
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
# sys.path
# =========================
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(MODULES_DIR))

# =========================
# Core（穩定）
# =========================
from core.engine import GuardianEngine
from core.data_manager import DataManager
from core.notifier import Notifier


# =========================
# 🔥 通用動態載入器
# =========================
def load_class(module_path: str, keyword: str):
    """
    從模組中載入第一個 class 名稱包含 keyword 的 class
    """
    module = importlib.import_module(module_path)

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__ and keyword in obj.__name__:
            print(f"[LOAD] {module_path}.{obj.__name__}")
            return obj

    raise ImportError(f"No class with keyword '{keyword}' found in {module_path}")


# =========================
# Modules（全部動態）
# =========================
from modules.scanners.news import NewsScanner

VIXScannerClass = load_class(
    "modules.scanners.vix_scanner",
    keyword="Scanner"
)

DefenseGuardianClass = load_class(
    "modules.guardians.defense",
    keyword="Guardian"
)

MarketAnalystClass = load_class(
    "modules.analysts.market_analyst",
    keyword="Analyst"
)


def main():
    engine = GuardianEngine(
        data_manager=DataManager(),
        notifier=Notifier(),
    )

    # Scanners
    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScannerClass())

    # Guardians
    engine.register_guardian(DefenseGuardianClass())

    # Analysts
    engine.register_analyst(MarketAnalystClass())

    engine.run()


if __name__ == "__main__":
    main()
