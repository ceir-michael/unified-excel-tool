from __future__ import annotations

import math
import os
import re
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from tkinter import filedialog


class OperationCancelled(RuntimeError):
    """Raised when the user requests cancellation between workbook operations."""


def check_cancelled(cancel) -> None:
    if cancel is not None and cancel():
        raise OperationCancelled("Operation cancelled. Existing output was not replaced.")


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
    blank = value is None or (isinstance(value, float) and math.isnan(value))
    base = "Blank" if blank else str(value).strip() or "Blank"
    base = re.sub(r'[:\\/?*\[\]\x00-\x1f]', "_", base).strip("'") or "Blank"
    candidate = f"{base}{suffix}"[:31]
    counter = 1
    folded = {name.casefold() for name in existing}

    while candidate.casefold() in folded:
        extra = f"_{counter}"
        candidate = f"{base}{suffix}"[: 31 - len(extra)] + extra
        counter += 1

    existing.add(candidate)
    return candidate


def safe_file_name(value) -> str:
    """Create a Windows-compatible filename component."""
    name = "Blank" if value is None else str(value).strip() or "Blank"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).rstrip(" .") or "Blank"
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if name.split(".", 1)[0].upper() in reserved:
        name = f"_{name}"
    return name[:180].rstrip(" .") or "Blank"


def paths_are_same(left: Path, right: Path) -> bool:
    """Compare paths safely even when the destination does not exist yet."""
    return os.path.normcase(str(left.expanduser().resolve())) == os.path.normcase(str(right.expanduser().resolve()))


def require_distinct_paths(input_path: Path, output_path: Path) -> None:
    if paths_are_same(input_path, output_path):
        raise ValueError("The output workbook must be different from the input workbook.")


@contextmanager
def atomic_output_path(destination: Path) -> Iterator[Path]:
    """Yield a same-directory staging path and publish it only on success."""
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f".{destination.stem}-{uuid.uuid4().hex}.tmp{destination.suffix}"
    )
    try:
        yield temporary
        os.replace(temporary, destination)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
