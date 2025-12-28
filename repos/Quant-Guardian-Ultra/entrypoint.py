# repos/Quant-Guardian-Ultra/entrypoint.py
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.notifier import DiscordNotifier
from core.engine import GuardianEngine
from modules.scanners.vix_scanner import VixScanner


def main():
    notifier = DiscordNotifier()

    # === 系統心跳（如果 webhook 有設就會送）===
    try:
        notifier.send_heartbeat(status="Phase 2：VIX Scanner 測試")
        print("[OK] Heartbeat sent")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    try:
        print("[PHASE 2] Initializing GuardianEngine ...")
        engine = GuardianEngine()
        print("[PHASE 2] GuardianEngine initialized")

        print("[PHASE 2] Initializing VIX Scanner ...")
        vix_scanner = VixScanner()
        print("[PHASE 2] VIX Scanner initialized")

        # 🔑 嘗試用最保守方式觸發 Scanner
        if hasattr(vix_scanner, "scan"):
            print("[PHASE 2] vix_scanner.scan()")
            result = vix_scanner.scan()
            print(f"[PHASE 2] VIX scan result: {result}")

        elif hasattr(vix_scanner, "run"):
            print("[PHASE 2] vix_scanner.run()")
            result = vix_scanner.run()
            print(f"[PHASE 2] VIX run result: {result}")

        else:
            print("[PHASE 2] VIX Scanner has no runnable method")

        print("[PHASE 2] VIX Scanner test completed")

    except Exception:
        print("[ERROR] Phase 2 failed")
        traceback.print_exc()


if __name__ == "__main__":
    main()
