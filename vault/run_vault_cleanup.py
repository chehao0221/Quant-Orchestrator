from vault.ai_vault_guard import AIVaultGuard

if __name__ == "__main__":
    guard = AIVaultGuard(
        policy_path="config/vault_policy.json"
    )
    deleted = guard.execute_cleanup()

    print(f"[VAULT] Deleted {len(deleted)} files safely.")
