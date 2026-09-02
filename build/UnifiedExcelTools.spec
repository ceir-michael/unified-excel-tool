# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

datas = []
datas += collect_data_files('customtkinter')
datas += [('README.md','.')]
try:
    datas += [('assets/icon.png','assets')]
except Exception:
    pass

hiddenimports = []
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('customtkinter')

a = Analysis(['main.py'], pathex=[], binaries=[], datas=datas,
             hiddenimports=hiddenimports)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,a.binaries,a.datas,name='UnifiedExcelTools',
          console=False, icon='assets/icon.ico')
