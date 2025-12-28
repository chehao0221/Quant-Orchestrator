# repos/Quant-Guardian-Ultra/entrypoint.py
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === 確保 base 在 sys.path ===
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# === 修復 modules 目錄尾巴空白（歷史地雷）===
modules_dir = os.path.join(BASE_DIR, "modules")
if os.path.isdir(modules_dir):
    for name in os.listdir(modules_dir):
        fixed = name.rstrip()
        if name != fixed:
            src = os.path.join(modules_dir, name)
            dst = os.path.join(modules_dir, fixed)
            if not os.path.exists(dst):
                os.rename(src, dst)
                print(f"[FIX] rename '{name}' -> '{fixed}'")

print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(modules_dir))

from core.notifier import DiscordNotifier
from core.engine import GuardianEngine
from modules.scanners.vix_scanner import VixScanner


def main():
    notifier = DiscordNotifier()

    # === 心跳 ===
    try:
        notifier.send_heartbeat(status="Phase 2：VIX Scanner 測試")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    try:
        print("[PHASE 2] Initializing GuardianEngine ...")
        engine = GuardianEngine()
        print("[PHASE 2] GuardianEngine initialized")

        print("[PHASE 2] Initializing VIX Scanner ...")
        vix = VixScanner()
        print("[PHASE 2] VIX Scanner initialized")

        # 嘗試最保守的執行方式
        if hasattr(vix, "scan"):
            print("[PHASE 2] vix.scan()")
            result = vix.scan()
            print("[PHASE 2] VIX result:", result)
        elif hasattr(vix, "run"):
            print("[PHASE 2] vix.run()")
            result = vix.run()
            print("[PHASE 2] VIX result:", result)
        else:
            print("[PHASE 2] VIX Scanner has no runnable method")

        print("[PHASE 2] completed")

    except Exception:
        print("[ERROR] Phase 2 failed")
        traceback.print_exc()


if __name__ == "__main__":
    main()
