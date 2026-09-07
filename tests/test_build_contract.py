import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildContractTests(unittest.TestCase):
    def test_packaging_includes_help_and_native_application_layouts(self):
        spec = (ROOT / "build" / "UnifiedExcelTools.spec").read_text(encoding="utf-8")
        self.assertIn('"INSTRUCTIONS.md"', spec)
        self.assertIn("COLLECT(", spec)
        self.assertIn("BUNDLE(", spec)
        self.assertIn("unified-excel-tools-version-info.txt", spec)
        self.assertNotIn("Path(WORKPATH)", spec)
        self.assertIn("icon_candidate.stat().st_size > 0", spec)

    def test_github_build_runs_tests_smoke_checks_and_releases(self):
        workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover", workflow)
        self.assertIn("Verify portable NumPy build", workflow)
        self.assertIn("numpy>=1.26.4,<2.4", requirements)
        self.assertIn("UNIFIED_EXCEL_TOOLS_SMOKE_TEST", workflow)
        self.assertIn('"./dist/Unified Excel Tools/Unified Excel Tools"', workflow)
        self.assertIn('"./dist/Unified Excel Tools.app/Contents/MacOS/Unified Excel Tools"', workflow)
        self.assertIn("gh release upload", workflow)
        self.assertIn("--prerelease", workflow)

    def test_workers_use_event_queue_instead_of_calling_tk(self):
        source = (ROOT / "ui" / "app.py").read_text(encoding="utf-8")
        worker = source.split("    def worker(", 1)[1].split("    def _poll_events", 1)[0]
        updater = source.split("    def _update_check_worker", 1)[1].split("    def _reset_update_button", 1)[0]
        self.assertIn("self.events.put", worker)
        self.assertIn("self.events.put", updater)
        self.assertNotIn("self.after", worker)
        self.assertNotIn("self.after", updater)

    def test_how_to_use_page_receives_the_full_content_area(self):
        app_source = (ROOT / "ui" / "app.py").read_text(encoding="utf-8")
        readme_source = (ROOT / "ui" / "readme_page.py").read_text(encoding="utf-8")
        show_page = app_source.split("    def show_page(", 1)[1].split("    def append_log", 1)[0]

        self.assertIn('help_visible = name == "How to Use"', show_page)
        self.assertIn("self.log_frame.grid_remove()", show_page)
        self.assertIn("self.log_frame.grid()", show_page)
        self.assertIn("class ReadmePage(ctk.CTkFrame)", readme_source)
        self.assertIn("self.grid_rowconfigure(2, weight=1)", readme_source)


if __name__ == "__main__":
    unittest.main()
