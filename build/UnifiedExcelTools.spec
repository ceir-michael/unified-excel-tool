# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


project_root = Path(SPECPATH).parent.resolve()

datas = collect_data_files("customtkinter")
datas += [(str(project_root / "ui" / "INSTRUCTIONS.md"), "ui")]

hiddenimports = []
hiddenimports += collect_submodules("openpyxl")
hiddenimports += collect_submodules("customtkinter")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UnifiedExcelTools",
    console=False,
    version=str(project_root / "build" / "version_info.txt")
    if sys.platform == "win32"
    else None,
)
app = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="UnifiedExcelTools",
)
