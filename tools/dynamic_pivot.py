from pathlib import Path
from typing import Callable

import pandas as pd


def run_dynamic_pivot(params: dict, log: Callable[[str], None]) -> str:
    """Pivot repeated values into numbered columns and save a new workbook."""
    input_path = Path(params["input_file"])
    output_path = Path(params["output_file"])
    source_sheet = params["source_sheet"]
    header_row = params["header_row"]
    key_column = params["key_column"]
    pivot_column = params["pivot_column"]

    if key_column == pivot_column:
        raise ValueError(
            "The row identifier column and pivot-value column must be different."
        )

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

    carry_columns = [column for column in df.columns if column != pivot_column]
    carry_columns = [key_column] + [
        column for column in carry_columns if column != key_column
    ]

    grouped = (
        df.groupby(carry_columns, dropna=False, sort=False)[pivot_column]
        .apply(list)
        .reset_index()
    )

    maximum = (
        int(grouped[pivot_column].map(len).max())
        if not grouped.empty
        else 0
    )
    safe_label = str(pivot_column).strip() or "Value"

    for index in range(maximum):
        grouped[f"{safe_label} {index + 1}"] = grouped[pivot_column].map(
            lambda values, i=index: values[i] if i < len(values) else None
        )

    grouped.drop(columns=[pivot_column], inplace=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Writing {len(grouped)} row(s) to {output_path.name}...")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        grouped.to_excel(writer, sheet_name="Pivoted Data", index=False)

    return f"Created {output_path}"
