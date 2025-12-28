# repos/Quant-Guardian-Ultra/entrypoint.py
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.notifier import DiscordNotifier
from core.engine import GuardianEngine


def main():
    notifier = DiscordNotifier()

    # === Phase 1：系統心跳（你已驗證 OK）===
    try:
        notifier.send_heartbeat(status="Phase 1：Engine 啟動測試")
        print("[OK] Heartbeat sent")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    # === Phase 1：只測試 Engine 是否能跑 ===
    try:
        print("[PHASE 1] Initializing GuardianEngine ...")
        engine = GuardianEngine()

        print("[PHASE 1] GuardianEngine initialized")

        # 🔍 嘗試找可執行入口（不假設 API）
        if hasattr(engine, "run"):
            print("[PHASE 1] engine.run()")
            engine.run()

        elif hasattr(engine, "execute"):
            print("[PHASE 1] engine.execute()")
            engine.execute()

        elif hasattr(engine, "step"):
            print("[PHASE 1] engine.step()")
            engine.step()

        else:
            print(
                "[PHASE 1] GuardianEngine instantiated, "
                "but no runnable method found (run / execute / step)"
            )

        print("[PHASE 1] Engine test completed")

    except Exception:
        print("[ERROR] Engine execution failed")
        traceback.print_exc()


if __name__ == "__main__":
    main()
