import os
import time

COLD_DAYS = 90  # 可調，但不是 0
NOW = time.time()

def is_cold(path):
    last_access = os.path.getatime(path)
    days = (NOW - last_access) / 86400
    return days >= COLD_DAYS


def clean_dir(root):
    for base, _, files in os.walk(root):
        for f in files:
            p = os.path.join(base, f)
            if is_cold(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def run():
    targets = [
        r"E:\Quant-Vault\STOCK_DB",
        r"E:\Quant-Vault\TEMP_CACHE"
    ]

    for t in targets:
        if os.path.exists(t):
            clean_dir(t)
