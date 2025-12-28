# repos/Quant-Guardian-Ultra/entrypoint.py
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.notifier import DiscordNotifier


def main():
    notifier = DiscordNotifier()

    try:
        notifier.send_heartbeat(status="正常監控中")
        print("[OK] Guardian heartbeat sent")

    except Exception as e:
        print(f"[HEARTBEAT] 心跳通知失敗： {e}")


if __name__ == "__main__":
    main()
