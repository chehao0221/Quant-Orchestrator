# vault_init.py
# Quant Vault 初始化器（終極封頂・Windows 專用）
# 職責：
# - 在 Windows 上初始化 E:\Quant-Vault 實體結構
# - 只建資料夾與必要的空殼 JSON
# - ❌ 不跑市場 ❌ 不學習 ❌ 不發通知 ❌ 不寫回測數據
# - 目的：讓整個量化系統「有地方可以正確落地」

import os
import json
from datetime import datetime

# =================================================
# 鐵律：實體 Vault 路徑（Windows）
# =================================================
VAULT_ROOT = r"E:\Quant-Vault"

# =================================================
# Vault 結構定義（一次封頂）
# =================================================
DIR_STRUCTURE = [
    # 原始事實層
    r"LOCKED_RAW\backtest\TW",
    r"LOCKED_RAW\backtest\US",
    r"LOCKED_RAW\backtest\JP",
    r"LOCKED_RAW\backtest\CRYPTO",
    r"LOCKED_RAW\signals",

    # 決策與治理層
    r"LOCKED_DECISION\guardian",
    r"LOCKED_DECISION\governance",

    # 學習層
    r"LEARNING\weights",
    r"LEARNING\logs",

    # 系統層
    r"SYSTEM\meta",
]

# =================================================
# 初始 JSON 檔（只放「必須存在」的）
# =================================================
INITIAL_FILES = {
    r"LOCKED_DECISION\guardian\guardian_state.json": {
        "freeze": False,
        "level": "L0",
        "reason": None,
        "updated_at": None
    },
    r"SYSTEM\version.json": {
        "system": "Quant-Vault",
        "version": "1.0.0",
        "initialized_at": None
    }
}

# =================================================
# 核心邏輯
# =================================================

def ensure_dirs():
    for rel in DIR_STRUCTURE:
        path = os.path.join(VAULT_ROOT, rel)
        os.makedirs(path, exist_ok=True)

def ensure_files():
    for rel, content in INITIAL_FILES.items():
        path = os.path.join(VAULT_ROOT, rel)
        if not os.path.exists(path):
            content = dict(content)
            content["initialized_at"] = datetime.now().isoformat()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)

def main():
    print("🔧 Quant Vault 初始化開始")
    print(f"📍 Vault Root: {VAULT_ROOT}")

    ensure_dirs()
    ensure_files()

    print("✅ Vault 結構建立完成")
    print("📂 你現在可以直接打開 E:\\Quant-Vault 檢查實體資料夾")
    print("🧠 後續任何腳本只要『有寫檔』，就一定會出現在這裡")

if __name__ == "__main__":
    main()
