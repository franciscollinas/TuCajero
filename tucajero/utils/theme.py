from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor


def get_theme():
    """Retorna 'dark' si el tema del sistema es oscuro, 'light' si es claro"""
    try:
        app = QApplication.instance()
        if app:
            palette = app.palette()
            text_color = palette.color(QPalette.ColorRole.WindowText)
            return "dark" if text_color.lightness() < 128 else "light"
    except:
        pass
    return "light"


def texto_secundario():
    """Retorna color de texto secundario legible en modo claro y oscuro"""
    if get_theme() == "dark":
        return "#aaaaaa"
    else:
        return "#555555"


def texto_terciario():
    """Retorna color de texto terciario legible en modo claro y oscuro"""
    if get_theme() == "dark":
        return "#888888"
    else:
        return "#777777"


def fondo_widget():
    """Retorna color de fondo para widgets"""
    if get_theme() == "dark":
        return "#1e1e1e"
    else:
        return "#f5f5f5"


def fondo_input():
    """Retorna color de fondo para inputs"""
    if get_theme() == "dark":
        return "#2d2d2d"
    else:
        return "#ffffff"


def aplicar_label_secundario(label, font_size="12px", padding=""):
    """Aplica estilo de texto secundario legible a un QLabel"""
    color = texto_secundario()
    padding_css = f"padding: {padding};" if padding else ""
    label.setStyleSheet(f"color: {color}; font-size: {font_size}; {padding_css}")


def estilo_input():
    """Retorna estilo CSS para inputs legible en ambos temas"""
    bg = fondo_input()
    text = "#333333" if get_theme() == "light" else "#ffffff"
    border = "#cccccc" if get_theme() == "light" else "#555555"
    return f"padding: 8px; font-size: 13px; background-color: {bg}; color: {text}; border: 1px solid {border}; border-radius: 4px;"


def estilo_boton_secundario():
    """Retorna estilo CSS para botones secundarios"""
    if get_theme() == "dark":
        return "background-color: #555555; color: white; padding: 8px;"
    else:
        return "background-color: #95a5a6; color: white; padding: 8px;"


def estilo_boton_secundario_hover():
    """Retorna color hover para botones secundarios"""
    if get_theme() == "dark":
        return "#666666"
    else:
        return "#7f8c8d"


def set_stylesheet(widget, dark_style, light_style):
    """Aplica un estilo diferente según el tema"""
    style = dark_style if get_theme() == "dark" else light_style
    widget.setStyleSheet(style)
