def fmt_moneda(valor):
    """Formatea un número como moneda con separador de miles"""
    try:
        return f"${float(valor):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"
