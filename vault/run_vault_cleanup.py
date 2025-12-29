from vault.ai_vault_guard import AIVaultGuard

if __name__ == "__main__":
    guard = AIVaultGuard("E:/Quant-Vault")

    tw_deleted = guard.cleanup_market("TW")
    us_deleted = guard.cleanup_market("US")

    print(f"[VAULT] TW deleted {len(tw_deleted)} files")
    print(f"[VAULT] US deleted {len(us_deleted)} files")
