import os
import sys

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
# 啟動 Guardian（legacy：初始化即執行）
# =========================
from core.engine import GuardianEngine
from core.notifier import DiscordNotifier


def main():
    # 啟動 Guardian Engine（初始化即執行）
    GuardianEngine()

    # =========================
    # 🫀 每日心跳通知（繁體中文）
    # =========================
    try:
        notifier = DiscordNotifier()
        notifier.send_heartbeat(
            status="正常監控中",
            note="系統已完成本次例行檢查，未偵測到異常風險。"
        )
        print("[HEARTBEAT] 心跳通知已送出")
    except Exception as e:
        print("[HEARTBEAT] 心跳通知失敗：", e)


if __name__ == "__main__":
    main()
