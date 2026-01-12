from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
import tempfile

import pandas as pd
import pyreadstat


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).upper() for col in df.columns]
    df.reset_index(drop=True, inplace=True)
    return df


def load_xpt_path(path: Path, domain_override: str | None = None) -> Tuple[str, pd.DataFrame]:
    df, _meta = pyreadstat.read_xport(path)
    domain = (domain_override or path.stem).upper()
    return domain, _normalize(df)


def load_xpt_bytes(data: bytes, filename: str) -> Tuple[str, pd.DataFrame]:
    domain = Path(filename).stem.upper()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xpt") as temp_file:
        temp_file.write(data)
        temp_path = Path(temp_file.name)
    try:
        return load_xpt_path(temp_path, domain_override=domain)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def load_xpt_files(paths: list[Path]) -> Dict[str, pd.DataFrame]:
    tables: Dict[str, pd.DataFrame] = {}
    for path in paths:
        domain, df = load_xpt_path(path)
        tables[domain] = df
    return tables
