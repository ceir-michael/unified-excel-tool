"""Diagnostic logging for failures hidden by windowed application builds."""

from __future__ import annotations

import datetime as dt
import os
import sys
import tempfile
import traceback
from pathlib import Path


def diagnostic_log_path() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Logs"
    else:
        root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "unified-excel-tools" / "diagnostics.log"


def log_exception(context: str, exc: BaseException) -> Path | None:
    path = diagnostic_log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[{dt.datetime.now().astimezone().isoformat()}] {context}\n")
            handle.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return path
    except OSError:
        return None
