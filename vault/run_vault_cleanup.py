from vault.ai_vault_guard import AIVaultGuard

if __name__ == "__main__":
    guard = AIVaultGuard("config/vault_policy.json")
    deleted = guard.execute_cleanup()
    print(f"[VAULT] deleted {len(deleted)} cold files")
