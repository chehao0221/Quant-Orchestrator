import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)
sys.path.insert(0, PROJECT_ROOT)

from utils.vault_root_guard import assert_vault_ready
from scripts.guard_check import guardian_freeze_check

DISCORD_WEBHOOK_CRYPTO = os.getenv("DISCORD_WEBHOOK_CRYPTO")
MARKET = "CRYPTO"

def main():
    assert_vault_ready(DISCORD_WEBHOOK_CRYPTO)

    state = guardian_freeze_check()
    if state.get("freeze"):
        return

    print(f"[{MARKET}] AI report ready")

if __name__ == "__main__":
    main()
