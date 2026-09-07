import os
import sys

from core.diagnostics import log_exception


def run() -> int:
    try:
        from ui.app import App

        if os.environ.get("UNIFIED_EXCEL_TOOLS_SMOKE_TEST") == "1":
            return 0
        app = App()
    except Exception as exc:
        log_path = log_exception("Unified Excel Tools could not start", exc)
        diagnostic = f"\n\nDiagnostic log: {log_path}" if log_path else ""
        print(f"Unified Excel Tools could not start: {exc}{diagnostic}", file=sys.stderr)
        try:
            from tkinter import messagebox

            messagebox.showerror("Unified Excel Tools could not start", f"{exc}{diagnostic}")
        except Exception:
            pass
        return 1
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
