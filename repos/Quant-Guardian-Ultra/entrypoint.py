# repos/Quant-Guardian-Ultra/entrypoint.py
import os
import sys
import traceback
import inspect
import importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# === 修復 modules 目錄尾巴空白（保險）===
modules_dir = os.path.join(BASE_DIR, "modules")
for name in os.listdir(modules_dir):
    fixed = name.rstrip()
    if name != fixed:
        os.rename(
            os.path.join(modules_dir, name),
            os.path.join(modules_dir, fixed),
        )
        print(f"[FIX] rename '{name}' -> '{fixed}'")

print("[DEBUG] modules contents =", os.listdir(modules_dir))

from core.notifier import DiscordNotifier
from core.engine import GuardianEngine
from modules.scanners.vix_scanner import VixScanner


def load_defense_class():
    module = importlib.import_module("modules.guardians.defense")
    for _, obj in inspect.getmembers(module, inspect.isclass):
        name = obj.__name__.lower()
        if "defense" in name or "guardian" in name:
            print(f"[LOAD] Defense class: {obj.__name__}")
            return obj
    raise ImportError("No Defense class found in modules.guardians.defense")


def main():
    notifier = DiscordNotifier()

    # === 心跳 ===
    try:
        notifier.send_heartbeat(status="Phase 3：黑天鵝防禦測試")
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    try:
        print("[PHASE 3] Initializing Engine / Scanner / Defense ...")

        engine = GuardianEngine()
        vix = VixScanner()

        DefenseClass = load_defense_class()
        defense = DefenseClass()

        print("[PHASE 3] Components initialized")

        # === 嘗試用最保守方式讓 Defense 評估 ===
        if hasattr(defense, "evaluate"):
            print("[PHASE 3] defense.evaluate(vix)")
            result = defense.evaluate(vix)

        elif hasattr(defense, "run"):
            print("[PHASE 3] defense.run(vix)")
            result = defense.run(vix)

        else:
            print("[PHASE 3] Defense has no runnable method")
            result = None

        print("[PHASE 3] Defense result:", result)

        # === 若結果顯示極端風險 → 黑天鵝通知 ===
        if result:
            notifier.send_black_swan(
                "🚨 **黑天鵝警報**\n\n"
                "偵測到極端市場風險（VIX / 防禦模組）。\n"
                "系統已進入防禦監控狀態。"
            )
            print("[PHASE 3] Black Swan alert sent")

        print("[PHASE 3] completed")

    except Exception:
        print("[ERROR] Phase 3 failed")
        traceback.print_exc()


if __name__ == "__main__":
    main()
