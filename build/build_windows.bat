@echo off
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
python -m PyInstaller --noconfirm --clean build\UnifiedExcelTools.spec
set UNIFIED_EXCEL_TOOLS_SMOKE_TEST=1
"dist\Unified Excel Tools\Unified Excel Tools.exe"
