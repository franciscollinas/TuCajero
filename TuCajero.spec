# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))
TUCajero_DIR = os.path.join(PROJECT_ROOT, "tucajero")

hiddenimports = [
    # SQLAlchemy
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.sql",
    "sqlalchemy.sql.elements",
    "sqlalchemy.engine",
    "sqlalchemy.ext.declarative",
    "sqlalchemy.ext.automap",
    "sqlalchemy.orm.decl_api",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.pool",
    
    # PySide6
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtPrintSupport",
    "shiboken6",
    
    # ReportLab
    "reportlab",
    "reportlab.graphics",
    "reportlab.platypus",
    "reportlab.lib.pagesizes",
    "reportlab.lib.units",
    "reportlab.lib.colors",
    "reportlab.lib.styles",
    "reportlab.lib.styles.getSampleStyleSheet",
    "reportlab.lib.enums",
    
    # Openpyxl
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",
    "openpyxl.writer.excel",
    
    # App modules
    "services.corte_service",
    "services.producto_service",
    "services.historial_service",
    "services.categoria_service",
    "utils.backup",
    "utils.recovery",
    "utils.post_close_validator",
    "utils.factura_diaria",
    "utils.excel_exporter",
    "utils.ticket",
    "utils.icon_helper",
    "utils.store_config",
    "security.license_manager",
]

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

pyside6_datas = collect_data_files("PySide6")
sqlalchemy_datas = collect_data_files("sqlalchemy")

# Collect app assets
assets_src = os.path.join(TUCajero_DIR, "assets")
app_datas = []
if os.path.exists(assets_src):
    for root, dirs, files in os.walk(assets_src):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join("assets", os.path.relpath(root, assets_src))
            app_datas.append((src, dst))

a = Analysis(
    [os.path.join(TUCajero_DIR, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=pyside6_datas + sqlalchemy_datas + app_datas,
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
        "PIL",
        "cv2",
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
