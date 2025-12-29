from pathlib import Path
import json

def write_pool(
    market_root: Path,
    pool_name: str,
    symbols: list[str]
):
    pool_dir = market_root / pool_name
    pool_dir.mkdir(parents=True, exist_ok=True)

    path = pool_dir / "latest.json"
    path.write_text(
        json.dumps(
            {
                "symbols": symbols,
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )
