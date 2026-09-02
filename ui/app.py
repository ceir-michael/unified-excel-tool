import os
import subprocess
import sys
import threading
import traceback
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from constants import (
    APP_NAME,
    APP_ORGANIZATION,
    APP_VERSION,
    CONTROL_HEIGHT,
    SIDEBAR_WIDTH,
)
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

        self.grid_columnconfigure(0, minsize=SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self._build_pages()
        self._build_log_area()
        self.show_page(self.current_name)

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

        ctk.CTkLabel(
            self.sidebar,
            text=f"{APP_VERSION} | © {APP_ORGANIZATION}",
            anchor="w",
        ).grid(
            row=30,
            column=0,
            sticky="ew",
            padx=16,
            pady=(10, 5),
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

        for button_name, button in self.nav_buttons.items():
            button.configure(
                fg_color=("#3B8ED0", "#1F6AA5")
                if button_name == name
                else "transparent"
            )

        self.run_button.configure(state="normal" if task else "disabled")

    def append_log(self, text):
        def update():
            self.log.insert("end", text + "\n")
            self.log.see("end")

        self.after(0, update)

    def run_selected(self):
        page, task = self.pages[self.current_name]
        if task is None:
            return

        try:
            params = page.values()
        except Exception as exc:
            messagebox.showwarning("Invalid Input", str(exc))
            return

        self.log.delete("1.0", "end")
        self.status.configure(text=f"Running {self.current_name}...")
        self.run_button.configure(state="disabled")
        self.progress.start()

        threading.Thread(
            target=self.worker,
            args=(task, params),
            daemon=True,
        ).start()

    def worker(self, task, params):
        try:
            result = task(params, self.append_log)

            if "output_folder" in params:
                self.last_folder = Path(params["output_folder"])
            elif "output_file" in params:
                self.last_folder = Path(params["output_file"]).parent
            else:
                self.last_folder = Path(params["input_file"]).parent

            self.after(0, lambda: self.success(result))
        except Exception:
            details = traceback.format_exc()
            self.append_log(details)
            self.after(0, lambda: self.failure(details))

    def success(self, result):
        self.progress.stop()
        self.progress.set(0)
        self.status.configure(text="Completed")

        current_task = self.pages[self.current_name][1]
        self.run_button.configure(
            state="normal" if current_task is not None else "disabled"
        )
        self.open_button.configure(state="normal")
        messagebox.showinfo("Completed", result)

    def failure(self, details):
        self.progress.stop()
        self.progress.set(0)
        self.status.configure(text="Failed")

        current_task = self.pages[self.current_name][1]
        self.run_button.configure(
            state="normal" if current_task is not None else "disabled"
        )
        messagebox.showerror(
            "Processing Failed",
            details.strip().splitlines()[-1],
        )

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
