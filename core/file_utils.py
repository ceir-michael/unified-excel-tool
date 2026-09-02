from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
from tkinter import filedialog


def resource_path(filename: str) -> Path:
    """Return a bundled resource path for normal Python and PyInstaller runs."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / filename


def choose_excel_file(xlsx_only: bool = False) -> str:
    filetypes = (
        [("Excel Workbooks", "*.xlsx")]
        if xlsx_only
        else [("Excel Workbooks", "*.xlsx *.xls")]
    )
    return filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=filetypes,
    )


def safe_sheet_name(value, existing: set[str], suffix: str = "") -> str:
    """Create a unique worksheet name that complies with Excel restrictions."""
    base = "Blank" if pd.isna(value) else str(value).strip() or "Blank"
    base = re.sub(r'[:\/?*\[\]]', "_", base)
    candidate = f"{base}{suffix}"[:31]
    counter = 1

    while candidate in existing:
        extra = f"_{counter}"
        candidate = f"{base}{suffix}"[: 31 - len(extra)] + extra
        counter += 1

    existing.add(candidate)
    return candidate


def safe_file_name(value) -> str:
    """Create a Windows-compatible filename component."""
    name = "Blank" if value is None else str(value).strip() or "Blank"
    return re.sub(r'[<>:"/\|?*]', "_", name)
