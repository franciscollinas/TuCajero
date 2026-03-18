import os
import sys
from PySide6.QtGui import QIcon, QPixmap


def get_app_icon():
    """
    Retorna el QIcon de la app.
    Prioridad:
    1. Logo configurado por el usuario en LOCALAPPDATA
    2. Logo en assets/store/logo.png
    3. cruzmedic.ico por defecto
    """
    from utils.store_config import get_logo_path

    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        pm = QPixmap(logo_path)
        if not pm.isNull():
            return QIcon(pm)

    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for candidate in [
        os.path.join(base, "assets", "store", "logo.png"),
        os.path.join(base, "assets", "icons", "cruzmedic.ico"),
    ]:
        if os.path.exists(candidate):
            icon = QIcon(candidate)
            if not icon.isNull():
                return icon

    return QIcon()
