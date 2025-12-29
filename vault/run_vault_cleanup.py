from vault.ai_vault_guard import AIVaultGuard

if __name__ == "__main__":
    guard = AIVaultGuard("config/vault_policy.json")
    guard.scan_and_clean()
