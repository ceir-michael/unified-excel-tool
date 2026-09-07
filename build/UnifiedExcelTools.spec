# -*- mode: python ; coding: utf-8 -*-
import sys
import re
import tempfile
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

PROJECT_ROOT = Path(SPECPATH).parent
sys.path.insert(0, str(PROJECT_ROOT))
from constants import APP_NAME, APP_ORGANIZATION, APP_VERSION

icon_candidate = PROJECT_ROOT / "assets" / ("icon.ico" if sys.platform == "win32" else "icon.icns") if sys.platform in ("win32", "darwin") else None
icon = icon_candidate if icon_candidate and icon_candidate.is_file() and icon_candidate.stat().st_size > 0 else None
version_resource = None
if sys.platform == "win32":
    numeric = [int(part) for part in re.match(r"^v?(\d+)\.(\d+)\.(\d+)", APP_VERSION).groups()] + [0]
    version_resource = Path(tempfile.gettempdir()) / "unified-excel-tools-version-info.txt"
    version_resource.parent.mkdir(parents=True, exist_ok=True)
    version_resource.write_text(
        f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={tuple(numeric)}, prodvers={tuple(numeric)}),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', {APP_ORGANIZATION!r}),
      StringStruct('FileDescription', {APP_NAME!r}),
      StringStruct('FileVersion', {APP_VERSION!r}),
      StringStruct('ProductName', {APP_NAME!r}),
      StringStruct('ProductVersion', {APP_VERSION!r}),
    ])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])]),
  ],
)\n""",
        encoding="utf-8",
    )
datas = collect_data_files("customtkinter") + [
    (str(PROJECT_ROOT / "README.md"), "."),
    (str(PROJECT_ROOT / "ui" / "INSTRUCTIONS.md"), "ui"),
]
hiddenimports = (
    collect_submodules("openpyxl")
    + collect_submodules("pandas")
    + collect_submodules("customtkinter")
)

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
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
    name="Unified Excel Tools",
    console=False,
    icon=str(icon) if icon else None,
    version=str(version_resource) if version_resource else None,
)
application = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="Unified Excel Tools",
)

if sys.platform == "darwin":
    application = BUNDLE(
        application,
        name="Unified Excel Tools.app",
        icon=str(icon) if icon else None,
        bundle_identifier="edu.uth.ceir.unified-excel-tools",
    )
