import os
import sys

# === 強制鎖定 Guardian Repo Root（最重要） ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Debug 保險（可留著，不影響）
print("[DEBUG] sys.path =", sys.path)

# === Core ===
from core.engine import GuardianEngine
from core.data_manager import DataManager
from core.notifier import Notifier

# === Modules ===
from modules.scanners.news import NewsScanner
from modules.scanners.vix_scanner import VIXScanner
from modules.guardians.defense import DefenseGuardian
from modules.analysts.market_analyst import MarketAnalyst


def main():
    data_manager = DataManager()
    notifier = Notifier()

    engine = GuardianEngine(
        data_manager=data_manager,
        notifier=notifier,
    )

    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScanner())
    engine.register_guardian(DefenseGuardian())
    engine.register_analyst(MarketAnalyst())

    engine.run()


if __name__ == "__main__":
    main()
