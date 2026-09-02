import customtkinter as ctk

from constants import LABEL_WIDTH


class FormPage(ctk.CTkScrollableFrame):
    def __init__(self, master, title, description):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 4))

        ctk.CTkLabel(
            self,
            text=description,
            wraplength=760,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 18))

        self.form = ctk.CTkFrame(self, corner_radius=10)
        self.form.grid(row=2, column=0, sticky="new", padx=4, pady=(0, 12))
        self.form.grid_columnconfigure(0, minsize=LABEL_WIDTH)
        self.form.grid_columnconfigure(1, weight=1, minsize=360)
        self.next_row = 0

    def add_row(self, label, widget, top_pad=8, bottom_pad=8):
        row = self.next_row
        self.next_row += 1

        ctk.CTkLabel(
            self.form,
            text=label,
            anchor="w",
            width=LABEL_WIDTH,
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=(18, 12),
            pady=(top_pad, bottom_pad),
        )

        widget.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=(top_pad, bottom_pad),
        )
        return row

    def add_action(self, button):
        row = self.next_row
        self.next_row += 1
        button.grid(row=row, column=1, sticky="e", padx=(0, 18), pady=(2, 10))
        return row
