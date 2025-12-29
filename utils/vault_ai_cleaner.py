from pathlib import Path
from vault.ai_vault_guard import AIVaultGuard

def run():
    guard = AIVaultGuard("config/vault_policy.json")
    deleted = guard.execute_cleanup()
    print(f"[VAULT] Deleted {len(deleted)} cold files")

if __name__ == "__main__":
    run()
