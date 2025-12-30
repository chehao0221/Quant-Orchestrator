# Vault 冷資料還原執行器（人工 or AI 觸發）

import sys
from vault_restore_manager import restore

def main():
    if len(sys.argv) != 3:
        print("Usage: restore <archive.zip> <target_dir>")
        return

    zip_name = sys.argv[1]
    target_dir = sys.argv[2]

    result = restore(zip_name, target_dir)

    if result["ok"]:
        print(f"RESTORE OK: {result['restored_to']}")
    else:
        print(f"RESTORE FAILED: {result['reason']}")

if __name__ == "__main__":
    main()
