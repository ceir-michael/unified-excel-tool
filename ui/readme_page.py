import customtkinter as ctk
import re

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
        textbox._textbox.tag_config("h3", font=("Segoe UI", 13, "bold"), spacing1=8, spacing3=4)
        textbox._textbox.tag_config("list", font=("Segoe UI", 12), lmargin1=18, lmargin2=36)
        textbox._textbox.tag_config("bold", font=("Segoe UI", 12, "bold"))
        textbox._textbox.tag_config("code", font=("Consolas", 11), background="#333333")

        readme_path = resource_path("ui/INSTRUCTIONS.md")
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            self._insert_markdown(content)
        else:
            textbox.insert("end", "INSTRUCTIONS.md could not be found.\n", "body")

        textbox.configure(state="disabled")

    def _insert_markdown(self, content: str):
        """Render the lightweight Markdown used by the packaged help document."""
        inline = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*)")

        def insert_inline(value, base_tag):
            position = 0
            for match in inline.finditer(value):
                self.textbox.insert("end", value[position:match.start()], base_tag)
                token = match.group(0)
                tag = "code" if token.startswith("`") else "bold"
                width = 1 if tag == "code" else 2
                self.textbox.insert("end", token[width:-width], (base_tag, tag))
                position = match.end()
            self.textbox.insert("end", value[position:], base_tag)

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                insert_inline(stripped[2:], "h1")
            elif stripped.startswith("## "):
                insert_inline(stripped[3:], "h2")
            elif stripped.startswith("### "):
                insert_inline(stripped[4:], "h3")
            elif stripped.startswith(("- ", "* ")):
                insert_inline("•  " + stripped[2:], "list")
            elif match := re.match(r"^(\d+\.)\s+(.*)$", stripped):
                insert_inline(f"{match.group(1)}  {match.group(2)}", "list")
            elif stripped:
                insert_inline(stripped, "body")
            else:
                self.textbox.insert("end", "\n")
                continue
            self.textbox.insert("end", "\n")
