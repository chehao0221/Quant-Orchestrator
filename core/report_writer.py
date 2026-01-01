# core/report_writer.py
import os
import json
import time
import hashlib
from pathlib import Path
from typing import Literal, Optional


class ReportWriterError(Exception):
    pass


Market = Literal["TW", "US", "JP", "CRYPTO"]
FileKey = Literal["tw", "us", "jp", "crypto"]


class ReportWriter:
    """
    標準化結果輸出（唯一格式）
    --------------------------
    寫入位置：
      E:\\Quant-Vault\\TEMP_CACHE\\snapshot\\YYYY-MM-DD\\{market}.json

    特性：
    - schema 固定
    - 原子寫入
    - 防誤覆寫（同 hash 略過、不同 hash 預設拒絕）
    """

    _MARKET_TO_FILEKEY: dict[Market, FileKey] = {
        "TW": "tw",
        "US": "us",
        "JP": "jp",
        "CRYPTO": "crypto",
    }

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root).resolve()
        self.snapshot_root = (self.vault_root / "TEMP_CACHE" / "snapshot").resolve()
        self.snapshot_root.mkdir(parents=True, exist_ok=True)

    def write_report(
        self,
        market: Market,
        date_yyyy_mm_dd: str,
        strategy: str,
        metrics: dict,
        decision: Optional[dict] = None,
        run_id: Optional[str] = None,
        allow_overwrite: bool = False,
    ) -> Path:
        """
        metrics 必須包含：
          - return (float)          例：0.012
          - drawdown (float)        例：-0.034
          - volatility (float)      例：0.015
          - win_rate (float)        0~1
          - confidence (float)      0~1

        decision 可選：你當天的建議（例如標的、權重、方向等）
        """
        filekey = self._MARKET_TO_FILEKEY.get(market)
        if not filekey:
            raise ReportWriterError(f"不支援的 market: {market}")

        # 驗證 date 格式（最基本，避免亂資料夾）
        if not self._is_valid_date(date_yyyy_mm_dd):
            raise ReportWriterError(f"日期格式錯誤，需 YYYY-MM-DD：{date_yyyy_mm_dd}")

        validated = self._validate_metrics(metrics)

        report = {
            "meta": {
                "timestamp": int(time.time()),
                "market": market,
                "strategy": str(strategy),
                "date": date_yyyy_mm_dd,
                "run_id": run_id or f"{market}-{date_yyyy_mm_dd}",
            },
            "metrics": validated,
            "decision": decision or {},
        }

        day_dir = (self.snapshot_root / date_yyyy_mm_dd)
        day_dir.mkdir(parents=True, exist_ok=True)

        target = (day_dir / f"{filekey}.json")
        self._safe_write_json(target, report, allow_overwrite=allow_overwrite)
        return target

    # ---------- validation ----------

    @staticmethod
    def _validate_metrics(metrics: dict) -> dict:
        required = ["return", "drawdown", "volatility", "win_rate", "confidence"]
        for k in required:
            if k not in metrics:
                raise ReportWriterError(f"metrics 缺少欄位: {k}")

        def to_float(name: str) -> float:
            try:
                return float(metrics[name])
            except Exception:
                raise ReportWriterError(f"metrics[{name}] 必須是數字")

        r = to_float("return")
        dd = to_float("drawdown")
        vol = to_float("volatility")
        wr = to_float("win_rate")
        conf = to_float("confidence")

        if not (0.0 <= wr <= 1.0):
            raise ReportWriterError("win_rate 必須介於 0~1")
        if not (0.0 <= conf <= 1.0):
            raise ReportWriterError("confidence 必須介於 0~1")
        if vol < 0:
            raise ReportWriterError("volatility 不可為負數")

        # 統一小數精度（避免無限小數造成 hash 亂跳）
        return {
            "return": round(r, 8),
            "drawdown": round(dd, 8),
            "volatility": round(vol, 8),
            "win_rate": round(wr, 8),
            "confidence": round(conf, 8),
        }

    @staticmethod
    def _is_valid_date(s: str) -> bool:
        # 最小驗證：YYYY-MM-DD
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return False
        y, m, d = s.split("-")
        return y.isdigit() and m.isdigit() and d.isdigit()

    # ---------- safe write ----------

    @staticmethod
    def _hash_obj(obj: dict) -> str:
        raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _safe_write_json(self, path: Path, content: dict, allow_overwrite: bool) -> None:
        """
        - 若檔案不存在：直接寫
        - 若檔案存在：
            - hash 相同：略過（代表同結果，不吵）
            - hash 不同：
                - allow_overwrite=False：報錯（防誤覆寫）
                - allow_overwrite=True：覆寫
        """
        new_hash = self._hash_obj(content)

        if path.exists():
            try:
                old = json.loads(path.read_text(encoding="utf-8"))
                old_hash = self._hash_obj(old)
            except Exception:
                old_hash = None

            if old_hash == new_hash:
                return  # 同內容，略過

            if not allow_overwrite:
                raise ReportWriterError(
                    f"報告檔已存在且內容不同，預設禁止覆寫：{path}\n"
                    f"若確定要覆寫，請設 allow_overwrite=True"
                )

        self._atomic_write_json(path, content)

    @staticmethod
    def _atomic_write_json(path: Path, content: dict) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
