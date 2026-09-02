from pathlib import Path

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from constants import CONTROL_HEIGHT
from ui.base_page import FormPage
from ui.widgets import FilePicker


class WorkbookSplitterPage(FormPage):
    NO_TAB_OPTION = "<No tabs - one sheet per workbook>"

    def __init__(self, master):
        super().__init__(
            master,
            "Split Workbook into New Workbooks",
            "Create a separate workbook for each unique value in a selected column. "
            "Optionally create tabs inside each new workbook using another column.",
        )

        self.input_file = FilePicker(
            self.form,
            xlsx_only=True,
            command=self.default_folder,
        )
        self.header = ctk.CTkEntry(self.form, height=CONTROL_HEIGHT)
        self.header.insert(0, "1")
        self.split_column = ctk.CTkComboBox(
            self.form,
            values=["Load columns first"],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.tab_column = ctk.CTkComboBox(
            self.form,
            values=[self.NO_TAB_OPTION],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.tab_column.set(self.NO_TAB_OPTION)
        self.output_folder = FilePicker(self.form, folder=True)
        self.load_button = ctk.CTkButton(
            self.form,
            text="Load Columns",
            width=150,
            height=CONTROL_HEIGHT,
            command=self.load_columns,
        )

        self.add_row("Input .xlsx file", self.input_file, 18, 8)
        self.add_row("Header row number", self.header)
        self.add_row("Split into workbooks by", self.split_column)
        self.add_row("Optional tab column", self.tab_column)
        self.add_action(self.load_button)
        self.add_row("Output folder", self.output_folder, 8, 18)

    def default_folder(self, path):
        self.output_folder.set(Path(path).parent)
        self.reset_columns()

    def reset_columns(self):
        self.split_column.configure(values=["Load columns first"])
        self.split_column.set("Load columns first")
        self.tab_column.configure(values=[self.NO_TAB_OPTION])
        self.tab_column.set(self.NO_TAB_OPTION)

    def load_columns(self):
        try:
            if not self.input_file.get():
                raise ValueError("Select an input Excel file first.")

            header_row = int(self.header.get())
            if header_row < 1:
                raise ValueError("Header row must be 1 or greater.")

            columns = pd.read_excel(
                self.input_file.get(),
                header=header_row - 1,
                nrows=0,
            ).columns
            values = [str(column) for column in columns]

            if not values:
                raise ValueError("No columns were found in the selected header row.")

            self.split_column.configure(values=values)
            self.split_column.set(values[0])
            self.tab_column.configure(values=[self.NO_TAB_OPTION] + values)
            self.tab_column.set(self.NO_TAB_OPTION)
        except Exception as exc:
            messagebox.showerror("Unable to Load Columns", str(exc))

    def values(self):
        split_column = self.split_column.get()
        tab_column = self.tab_column.get()

        if split_column == "Load columns first":
            split_column = ""
        if tab_column == self.NO_TAB_OPTION:
            tab_column = None

        if not all(
            [self.input_file.get(), self.output_folder.get(), split_column]
        ):
            raise ValueError(
                "Select an input file, enter the header row, load/select the split "
                "column, and select an output folder."
            )

        if tab_column == split_column:
            raise ValueError(
                "The optional tab column must be different from the split column."
            )

        header_row = int(self.header.get())
        if header_row < 1:
            raise ValueError("Header row must be 1 or greater.")

        return {
            "input_file": self.input_file.get(),
            "header_row": header_row,
            "split_column": split_column,
            "tab_column": tab_column,
            "output_folder": self.output_folder.get(),
        }
