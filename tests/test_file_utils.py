import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.diagnostics import log_exception
from core.file_utils import (
    atomic_output_path,
    require_distinct_paths,
    safe_file_name,
    safe_sheet_name,
)


class FileUtilityTests(unittest.TestCase):
    def test_windows_file_names_and_case_insensitive_sheet_names_are_safe(self):
        self.assertEqual(safe_file_name(r"a\b."), "a_b")
        self.assertEqual(safe_file_name("CON"), "_CON")
        existing = set()
        self.assertEqual(safe_sheet_name("Alpha", existing), "Alpha")
        self.assertEqual(safe_sheet_name("alpha", existing), "alpha_1")

    def test_atomic_output_only_replaces_destination_on_success(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "result.xlsx"
            destination.write_text("old", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                with atomic_output_path(destination) as temporary:
                    temporary.write_text("partial", encoding="utf-8")
                    raise RuntimeError("failed")
            self.assertEqual(destination.read_text(encoding="utf-8"), "old")

            with atomic_output_path(destination) as temporary:
                temporary.write_text("new", encoding="utf-8")
            self.assertEqual(destination.read_text(encoding="utf-8"), "new")

    def test_source_cannot_be_selected_as_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "book.xlsx"
            with self.assertRaises(ValueError):
                require_distinct_paths(path, path)

    def test_diagnostic_log_contains_traceback(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"XDG_STATE_HOME": folder}):
            try:
                raise RuntimeError("example failure")
            except RuntimeError as exc:
                path = log_exception("Workbook job", exc)
            self.assertIsNotNone(path)
            self.assertIn("RuntimeError: example failure", Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
