from pathlib import Path
from tools.vault_ai_judge import ai_should_delete
from tools.vault_executor import safe_delete

def run_guard(file_meta_map: dict):
    for path_str, meta in file_meta_map.items():
        path = Path(path_str)
        if ai_should_delete(meta):
            safe_delete(path)
