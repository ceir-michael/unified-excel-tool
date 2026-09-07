from pathlib import Path
from typing import Callable

import pandas as pd

from core.file_utils import atomic_output_path, check_cancelled, require_distinct_paths, safe_sheet_name


def run_tab_splitter(params: dict, log: Callable[[str], None], cancel: Callable[[], bool] | None = None) -> str:
    input_path = Path(params["input_file"])
    output_path = Path(params["output_file"])
    require_distinct_paths(input_path, output_path)

    check_cancelled(cancel)
    df = pd.read_excel(input_path, header=params["header_row"] - 1)
    column = params["split_column"]

    if column not in df.columns:
        raise ValueError(f"Column '{column}' was not found.")

    existing: set[str] = set()

    with atomic_output_path(output_path) as temporary:
        with pd.ExcelWriter(temporary, engine="openpyxl") as writer:
            for value, subset in df.groupby(column, dropna=False, sort=False):
                check_cancelled(cancel)
                sheet = safe_sheet_name(value, existing)
                log(f"Writing {sheet}: {len(subset)} row(s)")
                subset.to_excel(writer, sheet_name=sheet, index=False)
        check_cancelled(cancel)

    return f"Created {output_path}"
