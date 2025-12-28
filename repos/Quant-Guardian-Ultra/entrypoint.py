import os
import sys
import inspect

# =========================
# 基本路徑
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")

# =========================
# 修復 modules 底下尾端空白資料夾
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
# 啟動 Guardian
# =========================
from core.engine import GuardianEngine


def main():
    engine = GuardianEngine()

    # 🔥 自動判斷可用入口（不假設 API）
    for method_name in ("run", "execute", "start"):
        if hasattr(engine, method_name):
            method = getattr(engine, method_name)
            if callable(method):
                print(f"[ENGINE] using GuardianEngine.{method_name}()")
                method()
                return

    # 如果真的都沒有
    raise RuntimeError(
        "GuardianEngine has no runnable entrypoint "
        "(expected one of: run / execute / start)"
    )


if __name__ == "__main__":
    main()
