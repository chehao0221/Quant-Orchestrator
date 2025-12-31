# bootstrap.py
# 終極 Root 注入器（一次解三 Repo）

import sys
from pathlib import Path

def inject_orchestrator_root():
    """
    將 Quant-Orchestrator 根目錄注入 sys.path
    不論從哪個子 repo / script 執行，都能正確 import
    """
    here = Path(__file__).resolve()

    # Quant-Orchestrator 本身
    orchestrator_root = here.parent

    if str(orchestrator_root) not in sys.path:
        sys.path.insert(0, str(orchestrator_root))

# 自動執行
inject_orchestrator_root()
