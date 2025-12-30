# 掃描 Vault 中的冷資料（不做任何刪除）

import os
import time

COLD_DAYS = 180
NOW = time.time()

def scan(path: str):
    cold_files = []

    for root, _, files in os.walk(path):
        if "LOCKED_" in root:
            continue

        for f in files:
            full = os.path.join(root, f)
            try:
                last_access = os.path.getatime(full)
            except OSError:
                continue

            age_days = (NOW - last_access) / 86400
            if age_days >= COLD_DAYS:
                cold_files.append({
                    "path": full,
                    "age_days": int(age_days)
                })

    return cold_files
