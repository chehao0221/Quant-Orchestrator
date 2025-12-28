import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 修正資料夾名稱尾巴空白（歷史問題）
for name in ["modules", "modules/scanners", "modules/guardians", "modules/analysts"]:
    p = BASE_DIR / name
    if p.exists() and p.name.endswith(" "):
        fixed = p.with_name(p.name.strip())
        p.rename(fixed)
        print(f"[FIX] rename '{p.name}' -> '{fixed.name}'")

print("[DEBUG] sys.path =", sys.path)
print("[DEBUG] modules contents =", os.listdir(BASE_DIR / "modules"))

from core.notifier import Notifier
from modules.scanners.vix_scanner import VixScanner
from modules.guardians.defense import DefenseManager


def main():
    notifier = Notifier()

    # 心跳（不因 webhook 未設而中斷）
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

    if result["level"] in ["L3", "L4"]:
        notifier.send(
            f"⚠️ 風險警示\nVIX={vix_value}\n等級={result['level']}\n動作={result['action']}",
            channel="black_swan",
        )


if __name__ == "__main__":
    main()
