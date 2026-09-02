from pathlib import Path
from typing import Callable

import pandas as pd

from core.file_utils import safe_sheet_name


def run_tab_splitter(params: dict, log: Callable[[str], None]) -> str:
    input_path = Path(params["input_file"])
    output_path = Path(params["output_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(input_path, header=params["header_row"] - 1)
    column = params["split_column"]

    if column not in df.columns:
        raise ValueError(f"Column '{column}' was not found.")

    existing: set[str] = set()

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for value, subset in df.groupby(column, dropna=False, sort=False):
            sheet = safe_sheet_name(value, existing)
            log(f"Writing {sheet}: {len(subset)} row(s)")
            subset.to_excel(writer, sheet_name=sheet, index=False)

    return f"Created {output_path}"
