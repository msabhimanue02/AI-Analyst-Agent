"""Utilities to export structured records to downstream sinks."""

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR

def export_to_csv(records, filename="final.csv"):
    out_path = Path(PROCESSED_DIR) / filename
    df = pd.DataFrame(records)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return str(out_path)
