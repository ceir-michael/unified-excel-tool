import customtkinter as ctk
from tkinter import filedialog

from constants import CONTROL_HEIGHT
from core.file_utils import choose_excel_file


class FilePicker(ctk.CTkFrame):
    def __init__(
        self,
        master,
        folder=False,
        save=False,
        xlsx_only=False,
        command=None,
    ):
        super().__init__(master, fg_color="transparent", height=CONTROL_HEIGHT)
        self.folder = folder
        self.save = save
        self.xlsx_only = xlsx_only
        self.command = command

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self, height=CONTROL_HEIGHT)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.button = ctk.CTkButton(
            self,
            text="Browse...",
            width=105,
            height=CONTROL_HEIGHT,
            command=self.browse,
        )
        self.button.grid(row=0, column=1, sticky="e")

    def browse(self):
        if self.folder:
            path = filedialog.askdirectory(
                title="Select Output Folder",
                initialdir=self.get() or None,
            )
        elif self.save:
            path = filedialog.asksaveasfilename(
                title="Save Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel Workbook", "*.xlsx")],
            )
        else:
            path = choose_excel_file(self.xlsx_only)

        if path:
            self.set(path)
            if self.command:
                self.command(path)

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
