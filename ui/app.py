import os
import subprocess
import sys
import threading
import traceback
import webbrowser
from pathlib import Path
from queue import Empty, Queue
from threading import Event

import customtkinter as ctk
from tkinter import messagebox

from constants import (
    APP_NAME,
    APP_ORGANIZATION,
    APP_VERSION,
    CONTROL_HEIGHT,
    SIDEBAR_WIDTH,
)
from core.diagnostics import log_exception
from core.file_utils import OperationCancelled
from core.update_checker import UpdateCheckError, check_for_updates
from tools.dynamic_pivot import run_dynamic_pivot
from tools.tab_splitter import run_tab_splitter
from tools.workbook_splitter import run_workbook_splitter
from ui.pivot_page import PivotPage
from ui.readme_page import ReadmePage
from ui.tab_splitter_page import TabSplitterPage
from ui.workbook_splitter_page import WorkbookSplitterPage


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1180x780")
        self.minsize(980, 680)

        self.last_folder: Path | None = None
        self.current_name = "How to Use"
        self.nav_buttons = {}
        self.events: Queue[tuple] = Queue()
        self.active_job: str | None = None
        self.cancel_event = Event()
        self.worker_thread: threading.Thread | None = None
        self.close_when_finished = False

        self.grid_columnconfigure(0, minsize=SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self._build_pages()
        self._build_log_area()
        self.show_page(self.current_name)
        self.protocol("WM_DELETE_WINDOW", self.request_close)
        self.after(50, self._poll_events)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(20, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text=APP_NAME,
            font=ctk.CTkFont(size=21, weight="bold"),
            wraplength=235,
            justify="left",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(26, 20),
        )

        tool_names = [
            "How to Use",
            "Split into Tabs",
            "Split into Workbooks",
            "Dynamic Pivot Worksheet",
        ]

        for row, name in enumerate(tool_names, start=1):
            button = ctk.CTkButton(
                self.sidebar,
                text=name,
                anchor="w",
                height=42,
                command=lambda page_name=name: self.show_page(page_name),
            )
            button.grid(row=row, column=0, sticky="ew", padx=14, pady=5)
            self.nav_buttons[name] = button

        self.update_button = ctk.CTkButton(
            self.sidebar,
            text="Check for Updates",
            height=34,
            command=self.start_update_check,
        )
        self.update_button.grid(
            row=29,
            column=0,
            sticky="ew",
            padx=14,
            pady=(10, 5),
        )

        ctk.CTkLabel(
            self.sidebar,
            text=f"{APP_VERSION} | © {APP_ORGANIZATION}",
            anchor="w",
        ).grid(
            row=30,
            column=0,
            sticky="ew",
            padx=16,
            pady=(5, 12),
        )

    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=22,
            pady=18,
        )
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=3)
        self.content.grid_rowconfigure(1, weight=2)

        self.page_host = ctk.CTkFrame(self.content, fg_color="transparent")
        self.page_host.grid(row=0, column=0, sticky="nsew")
        self.page_host.grid_columnconfigure(0, weight=1)
        self.page_host.grid_rowconfigure(0, weight=1)

    def _build_pages(self):
        self.pages = {
            "How to Use": (ReadmePage(self.page_host), None),
            "Split into Tabs": (
                TabSplitterPage(self.page_host),
                run_tab_splitter,
            ),
            "Split into Workbooks": (
                WorkbookSplitterPage(self.page_host),
                run_workbook_splitter,
            ),
            "Dynamic Pivot Worksheet": (
                PivotPage(self.page_host),
                run_dynamic_pivot,
            ),
        }

        for page, _ in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

    def _build_log_area(self):
        self.log_frame = ctk.CTkFrame(self.content)
        self.log_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(14, 0),
        )
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        status_row = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        status_row.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(8, 6),
        )
        status_row.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(status_row, text="Ready", anchor="w")
        self.status.grid(row=0, column=0, sticky="ew")

        self.progress = ctk.CTkProgressBar(
            status_row,
            mode="indeterminate",
            width=220,
        )
        self.progress.grid(row=0, column=1, padx=(10, 0))
        self.progress.set(0)

        self.log = ctk.CTkTextbox(self.log_frame, wrap="word")
        self.log.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=6,
        )

        action_row = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        action_row.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )
        action_row.grid_columnconfigure(1, weight=1)

        self.open_button = ctk.CTkButton(
            action_row,
            text="Open Output Folder",
            height=CONTROL_HEIGHT,
            state="disabled",
            command=self.open_folder,
        )
        self.open_button.grid(row=0, column=0, sticky="w")

        self.cancel_button = ctk.CTkButton(
            action_row,
            text="Cancel",
            height=CONTROL_HEIGHT,
            state="disabled",
            command=self.cancel_job,
        )
        self.cancel_button.grid(row=0, column=1, sticky="e", padx=(10, 12))

        self.run_button = ctk.CTkButton(
            action_row,
            text="Run Selected Tool",
            height=CONTROL_HEIGHT,
            command=self.run_selected,
        )
        self.run_button.grid(row=0, column=2, sticky="e")

    def show_page(self, name):
        for page, _ in self.pages.values():
            page.grid_remove()

        page, task = self.pages[name]
        page.grid(row=0, column=0, sticky="nsew")
        self.current_name = name

        help_visible = name == "How to Use"
        if help_visible:
            self.log_frame.grid_remove()
            self.content.grid_rowconfigure(0, weight=1)
            self.content.grid_rowconfigure(1, weight=0)
        else:
            self.log_frame.grid()
            self.content.grid_rowconfigure(0, weight=3)
            self.content.grid_rowconfigure(1, weight=2)

        for button_name, button in self.nav_buttons.items():
            button.configure(
                fg_color=("#3B8ED0", "#1F6AA5")
                if button_name == name
                else "transparent"
            )

        self.run_button.configure(
            state="normal" if task and self.active_job is None else "disabled"
        )

    def append_log(self, text):
        self.events.put(("log", str(text)))

    def run_selected(self):
        if self.active_job is not None:
            messagebox.showwarning(
                "Operation in Progress",
                f"Wait for '{self.active_job}' to finish or cancel it before starting another tool.",
            )
            return
        page, task = self.pages[self.current_name]
        if task is None:
            return

        try:
            params = page.values()
        except Exception as exc:
            messagebox.showwarning("Invalid Input", str(exc))
            return

        if self.current_name in ("Split into Tabs", "Dynamic Pivot Worksheet"):
            proceed = messagebox.askokcancel(
                "Workbook Feature Notice",
                "This operation creates a new tabular workbook. Original formulas, formatting, "
                "merged cells, validation rules, images, and macros are not preserved.\n\nContinue?",
            )
        else:
            proceed = messagebox.askokcancel(
                "Workbook Feature Notice",
                "Basic cell styles, comments, hyperlinks, and column widths are copied. Other "
                "workbook features and formula references may require review.\n\nContinue?",
            )
        if not proceed:
            return
        output_file = params.get("output_file")
        if output_file and Path(output_file).exists() and not messagebox.askyesno(
            "Replace Existing Output?",
            f"Replace the existing workbook?\n\n{Path(output_file).resolve()}",
            icon="warning",
            default="no",
        ):
            return

        self.log.delete("1.0", "end")
        self.status.configure(text=f"Running {self.current_name}...")
        self.active_job = self.current_name
        self.cancel_event.clear()
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal", text="Cancel")
        self.update_button.configure(state="disabled")
        self.progress.start()

        self.worker_thread = threading.Thread(
            target=self.worker,
            args=(task, params, self.current_name),
            daemon=False,
        )
        self.worker_thread.start()

    def worker(self, task, params, job_name):
        try:
            result = task(params, self.append_log, self.cancel_event.is_set)
        except BaseException as exc:
            details = traceback.format_exc()
            log_path = log_exception(f"{job_name} failed", exc)
            self.events.put(("failure", details, log_path, isinstance(exc, OperationCancelled)))
        else:
            self.events.put(("success", result, params, job_name))

    def _poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "log":
                    self.log.insert("end", event[1] + "\n")
                    self.log.see("end")
                elif kind == "success":
                    self.success(*event[1:])
                elif kind == "failure":
                    self.failure(*event[1:])
                elif kind == "update_success":
                    self._show_update_result(event[1])
                elif kind == "update_failure":
                    self._show_update_error(event[1], event[2])
        except Empty:
            pass
        if self.close_when_finished and self.active_job is None:
            return
        if self.winfo_exists():
            self.after(50, self._poll_events)

    def _finish_job(self):
        self.progress.stop()
        self.progress.set(0)
        self.active_job = None
        self.worker_thread = None
        self.cancel_event.clear()
        self.cancel_button.configure(state="disabled", text="Cancel")
        self.update_button.configure(state="normal")
        current_task = self.pages[self.current_name][1]
        self.run_button.configure(
            state="normal" if current_task is not None else "disabled"
        )
        if self.close_when_finished:
            self.destroy()
            return True
        return False

    def success(self, result, params, job_name):
        if "output_folder" in params:
            self.last_folder = Path(params["output_folder"])
        elif "output_file" in params:
            self.last_folder = Path(params["output_file"]).parent
        else:
            self.last_folder = Path(params["input_file"]).parent
        self.status.configure(text=f"Completed: {job_name}")
        if self._finish_job():
            return
        self.open_button.configure(state="normal")
        messagebox.showinfo("Completed", result)

    def failure(self, details, log_path, cancelled=False):
        self.log.insert("end", details + "\n")
        self.log.see("end")
        self.status.configure(text="Cancelled" if cancelled else "Failed")
        if self._finish_job():
            return
        if cancelled:
            messagebox.showinfo("Operation Cancelled", "The operation was cancelled. Existing output was not replaced.")
            return
        diagnostic = f"\n\nDiagnostic log: {log_path}" if log_path else ""
        messagebox.showerror("Processing Failed", details.strip().splitlines()[-1] + diagnostic)

    def cancel_job(self):
        if self.active_job is None:
            return
        self.cancel_event.set()
        self.cancel_button.configure(state="disabled", text="Cancelling...")
        self.status.configure(text=f"Cancelling {self.active_job} after the current workbook step...")

    def request_close(self):
        if self.active_job is None:
            self.destroy()
            return
        if messagebox.askyesno(
            "Operation in Progress",
            f"Cancel '{self.active_job}' and close after the current workbook step finishes?",
        ):
            self.close_when_finished = True
            self.cancel_job()

    def open_folder(self):
        if not self.last_folder:
            return

        folder = str(self.last_folder.resolve())
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except OSError as exc:
            messagebox.showerror("Unable to Open Folder", str(exc))

    def start_update_check(self):
        if self.active_job is not None:
            messagebox.showwarning("Operation in Progress", "Wait for the workbook operation to finish before checking for updates.")
            return
        self.update_button.configure(state="disabled", text="Checking...")
        threading.Thread(target=self._update_check_worker, daemon=True).start()

    def _update_check_worker(self):
        try:
            update_info = check_for_updates()
        except UpdateCheckError as exc:
            self.events.put(("update_failure", str(exc), None))
        except Exception as exc:
            self.events.put(("update_failure", "An unexpected error occurred while checking for updates.", log_exception("Update check failed", exc)))
        else:
            self.events.put(("update_success", update_info))

    def _reset_update_button(self):
        self.update_button.configure(state="normal", text="Check for Updates")

    def _show_update_error(self, error, log_path=None):
        self._reset_update_button()
        diagnostic = f"\n\nDiagnostic log: {log_path}" if log_path else ""
        messagebox.showerror("Unable to Check for Updates", error + diagnostic)

    def _show_update_result(self, update_info):
        self._reset_update_button()
        if not update_info.update_available:
            messagebox.showinfo(
                "No Updates Available",
                f"You're using the latest version ({APP_VERSION}).",
            )
            return

        open_release = messagebox.askyesno(
            "Update Available",
            f"{update_info.release_name} is available.\n\n"
            f"Installed version: {APP_VERSION}\n"
            f"Latest version: {update_info.latest_version}\n\n"
            "Open the download page?",
        )
        if open_release:
            webbrowser.open(update_info.release_url)
