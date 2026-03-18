"""
TuCajero Build Script
Genera un instalador personalizado para una tienda especifica.

Usage:
    python build_store.py
    python build_store.py "Mi Tienda"
    python build_store.py "Mi Tienda" "C:\logos\milogo.png"
"""

import os
import sys
import json
import subprocess
import shutil

STORE_CONFIG = {
    "store_name": "Farmacia CruzMedic",
    "logo_path": "assets/store/logo.png",
    "address": "Calle 10 #22-15",
    "phone": "+57 300 123 4567",
    "nit": "901234567",
}

LOGO_SOURCE = ""

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TUCajero_DIR = os.path.join(PROJECT_ROOT, "tucajero")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
ASSETS_STORE_DIR = os.path.join(TUCajero_DIR, "assets", "store")
CONFIG_FILE = os.path.join(TUCajero_DIR, "config", "store_config.json")


def clean_builds():
    """Limpia builds anteriores"""
    print("[1/5] Limpiando builds anteriores...")

    for folder in ["build", "dist"]:
        path = os.path.join(TUCajero_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".spec"):
                os.remove(os.path.join(root, file))

    os.makedirs(DIST_DIR)
    print()


def copy_logo():
    """Copia el logo de la tienda"""
    print("[2/5] Copiando logo...")

    if LOGO_SOURCE and os.path.exists(LOGO_SOURCE):
        os.makedirs(ASSETS_STORE_DIR, exist_ok=True)
        dest = os.path.join(ASSETS_STORE_DIR, "logo.png")
        shutil.copy2(LOGO_SOURCE, dest)
        print(f"   Logo: {LOGO_SOURCE} -> {dest}")
    else:
        print("   Sin logo (LOGO_SOURCE no configurado)")
    print()


def generate_config():
    """Genera configuracion de la tienda"""
    print("[3/5] Generando configuracion...")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(STORE_CONFIG, f, indent=2, ensure_ascii=False)

    print(f"   Config: {CONFIG_FILE}")
    print()


def build_executable():
    """Compila el executable con PyInstaller usando spec file"""
    print("[4/5] Compilando executable...")

    os.chdir(PROJECT_ROOT)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "TuCajero.spec",
    ]

    subprocess.run(cmd, check=True)

    exe_src = os.path.join("dist", "TuCajero.exe")
    exe_dst = os.path.join(DIST_DIR, "TuCajero.exe")

    if os.path.exists(exe_src):
        shutil.move(exe_src, exe_dst)
        print(f"   EXE: {exe_dst}")

    os.chdir(PROJECT_ROOT)
    print()


def create_installer():
    """Crea el instalador con Inno Setup"""
    print("[5/5] Generando instalador...")

    sanitized_name = STORE_CONFIG["store_name"].replace(" ", "")
    iss_file = "build_tucajero.iss"

    iss_content = f"""[Setup]
AppName=TuCajero - {STORE_CONFIG["store_name"]}
AppVersion=1.0
DefaultDirName={{autopf}}\\TuCajero
DefaultGroupName=TuCajero - {STORE_CONFIG["store_name"]}
OutputBaseFilename=TuCajero_{sanitized_name}_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\\TuCajero.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "tucajero\\assets\\*"; DestDir: "{{app}}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tucajero\\database\\*"; DestDir: "{{app}}\\database"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\TuCajero - {STORE_CONFIG["store_name"]}"; Filename: "{{app}}\\TuCajero.exe"
Name: "{{commondesktop}}\\TuCajero - {STORE_CONFIG["store_name"]}"; Filename: "{{app}}\\TuCajero.exe"

[Run]
Filename: "{{app}}\\TuCajero.exe"; Description: "Ejecutar TuCajero"; Flags: postinstall nowait skipifsilent
"""

    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_content)

    print(f"   ISS: {iss_file}")

    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    iscc = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc = path
            break

    if iscc:
        subprocess.run([iscc, iss_file], check=True)

        output_exe = f"Output\\TuCajero_{sanitized_name}_Setup.exe"
        if os.path.exists(output_exe):
            shutil.move(output_exe, os.path.join(DIST_DIR))
            print(f"   Installer: dist\\TuCajero_{sanitized_name}_Setup.exe")
            shutil.rmtree("Output", ignore_errors=True)

        os.remove(iss_file)
    else:
        print()
        print("   INSTALADOR: Inno Setup 6 no encontrado.")
        print("   Descarga desde: https://jrsoftware.org/isinfo.php")
        print(f'   Luego ejecuta: "<path>\\ISCC.exe" {iss_file}')

    print()


def main():
    """Funcion principal"""
    global STORE_CONFIG, LOGO_SOURCE

    if len(sys.argv) > 1:
        STORE_CONFIG["store_name"] = sys.argv[1]

    if len(sys.argv) > 2:
        LOGO_SOURCE = sys.argv[2]

    if len(sys.argv) > 3:
        STORE_CONFIG["address"] = sys.argv[3]

    if len(sys.argv) > 4:
        STORE_CONFIG["phone"] = sys.argv[4]

    if len(sys.argv) > 5:
        STORE_CONFIG["nit"] = sys.argv[5]

    print("=" * 50)
    print("TuCajero - Build Process")
    print("=" * 50)
    print()
    print("Configuracion de la tienda:")
    print(f"  Nombre:    {STORE_CONFIG['store_name']}")
    print(f"  Logo:      {LOGO_SOURCE or 'ninguno'}")
    print(f"  Direccion: {STORE_CONFIG['address']}")
    print(f"  Telefono:  {STORE_CONFIG['phone']}")
    print(f"  NIT:       {STORE_CONFIG['nit']}")
    print()

    clean_builds()
    copy_logo()
    generate_config()
    build_executable()
    create_installer()

    print("=" * 50)
    print("Build completado!")
    print("=" * 50)
    print()
    print("Archivos generados:")
    for f in os.listdir(DIST_DIR):
        print(f"  - dist/{f}")
    print()


if __name__ == "__main__":
    main()
