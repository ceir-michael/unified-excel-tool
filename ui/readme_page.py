import customtkinter as ctk

from core.file_utils import resource_path
from ui.base_page import FormPage


class ReadmePage(FormPage):
    def __init__(self, master):
        super().__init__(
            master,
            "How to Use",
            "Application documentation and usage instructions.",
        )

        self.form.grid_remove()
        self.grid_rowconfigure(2, weight=1)

        self.textbox = ctk.CTkTextbox(self, wrap="word")
        self.textbox.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=4,
            pady=(0, 12),
        )
        self._populate_readme()

    def _populate_readme(self):
        textbox = self.textbox
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")

        textbox._textbox.tag_config(
            "h1",
            font=("Segoe UI", 20, "bold"),
            spacing3=10,
        )
        textbox._textbox.tag_config(
            "h2",
            font=("Segoe UI", 15, "bold"),
            spacing1=10,
            spacing3=5,
        )
        textbox._textbox.tag_config(
            "body",
            font=("Segoe UI", 12),
            lmargin1=10,
            lmargin2=10,
        )

        readme_path = resource_path("README.md")
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            self._insert_markdown(content)
        else:
            textbox.insert("end", "README.md could not be found.\n", "body")

        textbox.configure(state="disabled")

    def _insert_markdown(self, content: str):
        """Render basic Markdown headings and paragraphs in the textbox."""
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                self.textbox.insert("end", stripped[2:] + "\n", "h1")
            elif stripped.startswith("## "):
                self.textbox.insert("end", stripped[3:] + "\n", "h2")
            elif stripped:
                self.textbox.insert("end", stripped + "\n", "body")
            else:
                self.textbox.insert("end", "\n")
