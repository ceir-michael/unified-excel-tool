from pathlib import Path
from typing import Callable

import pandas as pd

from core.file_utils import atomic_output_path, check_cancelled, require_distinct_paths


def run_dynamic_pivot(params: dict, log: Callable[[str], None], cancel: Callable[[], bool] | None = None) -> str:
    """Pivot repeated values into numbered columns and save a new workbook."""
    input_path = Path(params["input_file"])
    output_path = Path(params["output_file"])
    source_sheet = params["source_sheet"]
    header_row = params["header_row"]
    key_column = params["key_column"]
    pivot_column = params["pivot_column"]
    require_distinct_paths(input_path, output_path)

    if key_column == pivot_column:
        raise ValueError(
            "The row identifier column and pivot-value column must be different."
        )

    check_cancelled(cancel)
    log(f"Reading sheet '{source_sheet}' from {input_path.name}...")
    df = pd.read_excel(
        input_path,
        sheet_name=source_sheet,
        header=header_row - 1,
    )

    missing = [
        column
        for column in (key_column, pivot_column)
        if column not in df.columns
    ]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    carry_columns = [column for column in df.columns if column not in (key_column, pivot_column)]
    by_key = df.groupby(key_column, dropna=False, sort=False)
    conflicting = [
        str(column)
        for column in carry_columns
        if (by_key[column].nunique(dropna=False) > 1).any()
    ]
    if conflicting:
        raise ValueError(
            f"Rows with the same '{key_column}' contain different values in: "
            + ", ".join(conflicting)
            + ". Clean those values or use a more specific row identifier."
        )

    grouped = by_key[carry_columns].first().reset_index() if carry_columns else by_key.size().reset_index().drop(columns=[0])
    grouped[pivot_column] = list(by_key[pivot_column].apply(list))

    maximum = (
        int(grouped[pivot_column].map(len).max())
        if not grouped.empty
        else 0
    )
    safe_label = str(pivot_column).strip() or "Value"

    for index in range(maximum):
        check_cancelled(cancel)
        generated_column = f"{safe_label} {index + 1}"
        if generated_column in grouped.columns and generated_column != pivot_column:
            raise ValueError(
                f"The generated column '{generated_column}' already exists in the source data. Rename that source column before pivoting."
            )
        grouped[generated_column] = grouped[pivot_column].map(
            lambda values, i=index: values[i] if i < len(values) else None
        )

    grouped.drop(columns=[pivot_column], inplace=True)
    check_cancelled(cancel)
    log(f"Writing {len(grouped)} row(s) to {output_path.name}...")
    with atomic_output_path(output_path) as temporary:
        with pd.ExcelWriter(temporary, engine="openpyxl") as writer:
            grouped.to_excel(writer, sheet_name="Pivoted Data", index=False)
        check_cancelled(cancel)

    return f"Created {output_path}"
