#!/bin/bash
python3 -m pip install -r requirements-build.txt
pyinstaller --clean build/UnifiedExcelTools.spec
