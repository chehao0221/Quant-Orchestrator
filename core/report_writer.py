# core/report_writer.py
import json
import os
import time
from pathlib import Path
from typing import Dict, Literal, Optional


Market = Literal["TW", "US", "JP", "CRYPTO"]


class ReportWriter:
    """
    標準化結果輸出（唯一格式）
    寫入：E:\Quant-Vault\TEMP_CACHE\snapshot\YYYY-MM-DD\<MARKET>.json
    """

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()

    def write(
        self,
        date_key: str,
        market: Market,
        metrics: Dict,
        extra: Optional[Dict] = None,
    ) -> Path:
        base = self.vault_root / "TEMP_CACHE" / "snapshot" / date_key
        base.mkdir(parents=True, exist_ok=True)

        payload = {
            "metrics": {
                "return": float(metrics["return"]),
                "drawdown": float(metrics["drawdown"]),
                "volatility": float(metrics["volatility"]),
                "win_rate": float(metrics["win_rate"]),
                "confidence": float(metrics["confidence"]),
            },
            "extra": extra or {},
        }

        record = {
            "meta": {"timestamp": int(time.time()), "market": market},
            "data": payload,
        }

        p = base / f"{market}.json"
        tmp = p.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
        return p
