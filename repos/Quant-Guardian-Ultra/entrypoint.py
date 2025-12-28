import os
import sys
import importlib
import inspect

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
# Core imports（穩定）
# =========================
from core.engine import GuardianEngine
from core.data_manager import DataManager
from core.notifier import Notifier

# =========================
# 🔥 動態載入 Scanner（不再猜 class 名）
# =========================
def load_first_scanner(module_path: str):
    """
    載入模組中第一個 class 名包含 'Scanner' 的 class
    """
    module = importlib.import_module(module_path)

    for _, obj in inspect.getmembers(module, inspect.isclass):
        # 排除 import 進來的 class，只留本模組定義的
        if obj.__module__ == module.__name__ and "Scanner" in obj.__name__:
            print(f"[LOAD] {module_path}.{obj.__name__}")
            return obj

    raise ImportError(f"No Scanner class found in {module_path}")

# =========================
# Modules imports（穩定）
# =========================
from modules.scanners.news import NewsScanner
from modules.guardians.defense import DefenseGuardian
from modules.analysts.market_analyst import MarketAnalyst

# 🔥 VIX scanner 動態解析
VIXScannerClass = load_first_scanner("modules.scanners.vix_scanner")


def main():
    engine = GuardianEngine(
        data_manager=DataManager(),
        notifier=Notifier(),
    )

    # Scanners
    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScannerClass())

    # Guardians
    engine.register_guardian(DefenseGuardian())

    # Analysts
    engine.register_analyst(MarketAnalyst())

    engine.run()


if __name__ == "__main__":
    main()
