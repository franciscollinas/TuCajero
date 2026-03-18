# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))
TUCajero_DIR = os.path.join(PROJECT_ROOT, "tucajero")

hiddenimports = [
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.sql",
    "sqlalchemy.engine",
    "sqlalchemy.ext.declarative",
    "sqlalchemy.ext.automap",
    "sqlalchemy.orm.decl_api",
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

pyside6_datas = collect_data_files("PySide6")
sqlalchemy_datas = collect_data_files("sqlalchemy")

a = Analysis(
    [os.path.join(TUCajero_DIR, "main.py")],
    pathex=[],
    binaries=[],
    datas=pyside6_datas + sqlalchemy_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

py = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    py,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="TuCajero",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(TUCajero_DIR, "assets", "icons", "cruzmedic.ico"),
)
