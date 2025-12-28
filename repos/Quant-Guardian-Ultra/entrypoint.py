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
# Core
# =========================
from core.engine import GuardianEngine

# =========================
# 🔥 動態載入工具
# =========================
def load_first_class(module_path: str):
    module = importlib.import_module(module_path)
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            print(f"[LOAD] {module_path}.{obj.__name__}")
            return obj
    raise ImportError(f"No class found in {module_path}")


def load_class_with_keyword(module_path: str, keyword: str):
    module = importlib.import_module(module_path)
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__ and keyword in obj.__name__:
            print(f"[LOAD] {module_path}.{obj.__name__}")
            return obj
    raise ImportError(f"No class with keyword '{keyword}' found in {module_path}")


# =========================
# Modules（實際對齊你 repo）
# =========================
from modules.scanners.news import NewsScanner
VIXScannerClass = load_class_with_keyword(
    "modules.scanners.vix_scanner",
    keyword="Scanner"
)

DefenseClass = load_first_class(
    "modules.guardians.defense"
)

MarketAnalystClass = load_class_with_keyword(
    "modules.analysts.market_analyst",
    keyword="Analyst"
)


def main():
    # ✅ 正確的初始化方式（不傳任何參數）
    engine = GuardianEngine()

    # Scanners
    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScannerClass())

    # Guardians / Defense
    engine.register_guardian(DefenseClass())

    # Analysts
    engine.register_analyst(MarketAnalystClass())

    engine.run()


if __name__ == "__main__":
    main()
