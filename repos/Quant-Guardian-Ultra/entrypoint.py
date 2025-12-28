import sys
import os
from pathlib import Path

# =====================================================
# Phase 0 — 強制修正 modules 底下「尾端空白資料夾」
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"

if MODULES_DIR.exists():
    for item in MODULES_DIR.iterdir():
        if item.is_dir() and item.name.endswith(" "):
            fixed_path = item.with_name(item.name.rstrip())
            if not fixed_path.exists():
                item.rename(fixed_path)
                print(f"[FIX] rename '{item.name}' -> '{fixed_path.name}'")

# =====================================================
# Phase 1 — sys.path 設定（修完資料夾後再加）
# =====================================================

sys.path.insert(0, str(BASE_DIR))

print("[DEBUG] sys.path =", sys.path)
print(
    "[DEBUG] modules contents =",
    [p.name for p in (BASE_DIR / "modules").iterdir() if p.is_dir()],
)

# =====================================================
# Phase 2 — 安全 import（現在一定成功）
# =====================================================

from core.notifier import Notifier
from modules.scanners.vix_scanner import VixScanner
from modules.guardians.defense import DefenseManager


# =====================================================
# Phase 3 — 主流程
# =====================================================

def main():
    notifier = Notifier()

    # 心跳（Webhook 沒設也不炸）
    try:
        notifier.heartbeat()
    except Exception as e:
        print(f"[WARN] Heartbeat failed: {e}")

    print("[PHASE] 初始化 VIX Scanner")
    vix_scanner = VixScanner()
    vix_value = vix_scanner.scan()
    print(f"[INFO] VIX 指數：{vix_value}")

    print("[PHASE] 初始化 Defense Manager")
    defense = DefenseManager()
    result = defense.evaluate(vix_value)

    print("[RESULT] Defense 評估結果：", result)

    if result.get("level") in ["L3", "L4"]:
        notifier.send(
            f"⚠️ 風險警示\nVIX={vix_value}\n等級={result['level']}\n動作={result['action']}",
            channel="black_swan",
        )


if __name__ == "__main__":
    main()
