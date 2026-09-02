from pathlib import Path

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from constants import CONTROL_HEIGHT
from ui.base_page import FormPage
from ui.widgets import FilePicker


class PivotPage(FormPage):
    def __init__(self, master):
        super().__init__(
            master,
            "Dynamic Pivot Worksheet",
            "Choose the row identifier and the column whose repeated values should "
            "be spread across numbered columns. The result is saved as a new workbook.",
        )

        self.input_file = FilePicker(
            self.form,
            xlsx_only=True,
            command=self.input_changed,
        )
        self.header = ctk.CTkEntry(self.form, height=CONTROL_HEIGHT)
        self.header.insert(0, "1")
        self.source = ctk.CTkComboBox(
            self.form,
            values=["Load sheets first"],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.key_column = ctk.CTkComboBox(
            self.form,
            values=["Load columns first"],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.pivot_column = ctk.CTkComboBox(
            self.form,
            values=["Load columns first"],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.output_file = FilePicker(self.form, save=True)
        self.load_sheets_button = ctk.CTkButton(
            self.form,
            text="Load Sheet Names",
            width=150,
            height=CONTROL_HEIGHT,
            command=self.load_sheets,
        )
        self.load_columns_button = ctk.CTkButton(
            self.form,
            text="Load Columns",
            width=150,
            height=CONTROL_HEIGHT,
            command=self.load_columns,
        )

        self.add_row("Input .xlsx file", self.input_file, 18, 8)
        self.add_row("Header row number", self.header)
        self.add_row("Source sheet", self.source)
        self.add_action(self.load_sheets_button)
        self.add_row("Row identifier column", self.key_column)
        self.add_row("Column to pivot", self.pivot_column)
        self.add_action(self.load_columns_button)
        self.add_row("New output workbook", self.output_file, 8, 18)

    def input_changed(self, path):
        source = Path(path)
        self.output_file.set(source.with_name(source.stem + "_pivoted.xlsx"))
        self.source.configure(values=["Load sheets first"])
        self.source.set("Load sheets first")
        self.reset_columns()

    def reset_columns(self):
        placeholder = ["Load columns first"]
        self.key_column.configure(values=placeholder)
        self.key_column.set(placeholder[0])
        self.pivot_column.configure(values=placeholder)
        self.pivot_column.set(placeholder[0])

    def load_sheets(self):
        try:
            if not self.input_file.get():
                raise ValueError("Select an input Excel file first.")

            names = pd.ExcelFile(
                self.input_file.get(),
                engine="openpyxl",
            ).sheet_names

            if not names:
                raise ValueError("No worksheets were found.")

            self.source.configure(values=names)
            self.source.set(names[0])
            self.reset_columns()
        except Exception as exc:
            messagebox.showerror("Unable to Load Sheets", str(exc))

    def load_columns(self):
        try:
            if not self.input_file.get():
                raise ValueError("Select an input Excel file first.")
            if self.source.get() == "Load sheets first":
                raise ValueError("Load and select a source sheet first.")

            header_row = int(self.header.get())
            if header_row < 1:
                raise ValueError("Header row must be 1 or greater.")

            columns = pd.read_excel(
                self.input_file.get(),
                sheet_name=self.source.get(),
                header=header_row - 1,
                nrows=0,
            ).columns
            values = [str(column) for column in columns]

            if len(values) < 2:
                raise ValueError(
                    "At least two columns are required for this operation."
                )

            self.key_column.configure(values=values)
            self.key_column.set(values[0])
            self.pivot_column.configure(values=values)
            self.pivot_column.set(values[1])
        except Exception as exc:
            messagebox.showerror("Unable to Load Columns", str(exc))

    def values(self):
        source_sheet = self.source.get()
        key_column = self.key_column.get()
        pivot_column = self.pivot_column.get()

        if source_sheet == "Load sheets first":
            source_sheet = ""
        if key_column == "Load columns first":
            key_column = ""
        if pivot_column == "Load columns first":
            pivot_column = ""

        if not all(
            [
                self.input_file.get(),
                source_sheet,
                key_column,
                pivot_column,
                self.output_file.get(),
            ]
        ):
            raise ValueError(
                "Select the input workbook, source sheet, row identifier, pivot "
                "column, and output workbook."
            )

        if key_column == pivot_column:
            raise ValueError(
                "The row identifier and pivot column must be different."
            )

        header_row = int(self.header.get())
        if header_row < 1:
            raise ValueError("Header row must be 1 or greater.")

        return {
            "input_file": self.input_file.get(),
            "header_row": header_row,
            "source_sheet": source_sheet,
            "key_column": key_column,
            "pivot_column": pivot_column,
            "output_file": self.output_file.get(),
        }
