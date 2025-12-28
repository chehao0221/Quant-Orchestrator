import os
import sys

# === Orchestrator / Local execution safety ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# === Core ===
from core.engine import GuardianEngine
from core.notifier import DiscordNotifier
from core.data_manager import DataManager

# === Modules ===
from modules.scanners.news import NewsScanner
from modules.scanners.vix_scanner import VIXScanner
from modules.guardians.defense import DefenseGuardian
from modules.analysts.market_analyst import MarketAnalyst


def main():
    data_manager = DataManager()
    notifier = DiscordNotifier()

    engine = GuardianEngine(
        data_manager=data_manager,
        notifier=notifier,
    )

    # Scanners
    engine.register_scanner(NewsScanner())
    engine.register_scanner(VIXScanner())

    # Guardians
    engine.register_guardian(DefenseGuardian())

    # Analysts
    engine.register_analyst(MarketAnalyst())

    engine.run()


if __name__ == "__main__":
    main()
