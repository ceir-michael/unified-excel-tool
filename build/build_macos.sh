#!/bin/bash
python3 -m pip install -r requirements-build.txt
python3 -m unittest discover -s tests -v
python3 -m PyInstaller --noconfirm --clean build/UnifiedExcelTools.spec
UNIFIED_EXCEL_TOOLS_SMOKE_TEST=1 "./dist/Unified Excel Tools.app/Contents/MacOS/Unified Excel Tools"
