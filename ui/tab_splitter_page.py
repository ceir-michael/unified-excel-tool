from pathlib import Path

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from constants import CONTROL_HEIGHT
from ui.base_page import FormPage
from ui.widgets import FilePicker


class TabSplitterPage(FormPage):
    def __init__(self, master):
        super().__init__(
            master,
            "Split Workbook into Tabs",
            "Create one worksheet for each unique value in a selected column.",
        )

        self.input_file = FilePicker(self.form, command=self.default_output)
        self.header = ctk.CTkEntry(self.form, height=CONTROL_HEIGHT)
        self.header.insert(0, "2")
        self.column = ctk.CTkComboBox(
            self.form,
            values=["Load columns first"],
            height=CONTROL_HEIGHT,
            state="readonly",
        )
        self.output = FilePicker(self.form, save=True)
        self.load_button = ctk.CTkButton(
            self.form,
            text="Load Columns",
            width=150,
            height=CONTROL_HEIGHT,
            command=self.load_columns,
        )

        self.add_row("Input Excel file", self.input_file, 18, 8)
        self.add_row("Header row number", self.header)
        self.add_row("Split column", self.column)
        self.add_action(self.load_button)
        self.add_row("Output workbook", self.output, 8, 18)

    def default_output(self, path):
        source = Path(path)
        self.output.set(source.with_name(source.stem + "_split.xlsx"))

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

            self.column.configure(values=values)
            self.column.set(values[0])
        except Exception as exc:
            messagebox.showerror("Unable to Load Columns", str(exc))

    def values(self):
        value = self.column.get()
        if value == "Load columns first":
            value = ""

        if not all([self.input_file.get(), self.output.get(), value]):
            raise ValueError(
                "Select an input file, load a split column, and select an output file."
            )

        header_row = int(self.header.get())
        if header_row < 1:
            raise ValueError("Header row must be 1 or greater.")

        return {
            "input_file": self.input_file.get(),
            "header_row": header_row,
            "split_column": value,
            "output_file": self.output.get(),
        }
