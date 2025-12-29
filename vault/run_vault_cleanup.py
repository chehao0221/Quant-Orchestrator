from pathlib import Path
from vault.vault_meta_builder import build_meta
from vault.vault_ai_judge import ai_should_delete
from vault.vault_executor import safe_delete

def run_cleanup(root: Path):
    for p in root.rglob("*.json"):
        meta = build_meta(p)

        # 這些標記由你現有模組補
        meta.update({
            "in_universe": False,
            "in_recent_top5": False,
            "in_core_watch": False,
            "has_newer_version": True,
            "read_by_ai_7d": False,
            "top5_count": 0,
            "black_swan_related": False,
        })

        if ai_should_delete(meta):
            safe_delete(p)

if __name__ == "__main__":
    run_cleanup(Path("E:/Quant-Vault/STOCK_DB"))
