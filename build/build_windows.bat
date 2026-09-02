@echo off
python -m pip install -r requirements-build.txt
pyinstaller --clean build\UnifiedExcelTools.spec
