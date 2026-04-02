import os
from datetime import datetime
from tucajero.utils.store_config import (
    get_store_name,
    get_address,
    get_phone,
    get_nit,
    get_email,
    get_logo_path,
)


class GeneradorTicket:
    WIDTH = 40

    def __init__(self, nombre_tienda=None):
        self.nombre_tienda = nombre_tienda or get_store_name()

    def generar(self, venta, items):
        """Genera el texto del ticket"""
        IVA_RATE = 0.19
        lines = []
        lines.append("=" * self.WIDTH)
        store_name = get_store_name()
        if store_name:
            lines.append(f"{store_name.upper():^{self.WIDTH}}")
        address = get_address()
        if address:
            lines.append(f"{address:^{self.WIDTH}}")
        phone = get_phone()
        if phone:
            lines.append(f"Tel: {phone}")
        email = get_email()
        if email:
            lines.append(f"Email: {email}")
        nit = get_nit()
        if nit:
            lines.append(f"NIT: {nit}")
        lines.append("=" * self.WIDTH)
        lines.append(f"Fecha: {venta.fecha.strftime('%d/%m/%Y %I:%M %p')}")
        lines.append(f"Ticket #: {venta.id}")
        if getattr(venta, "metodo_pago", None):
            lines.append(f"Método: {venta.metodo_pago}")
        lines.append("-" * self.WIDTH)
        subtotal_total = 0
        iva_total = 0
        for item in items:
            producto = item.producto
            cantidad = item.cantidad
            precio = item.precio
            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2)
            total_item = round(subtotal + iva, 2)
            subtotal_total += subtotal
            iva_total += iva
            lines.append(f"{producto.nombre[:20]:<20} x{cantidad}")
            lines.append(
                f"Base:${precio:.2f} IVA:${iva / cantidad:.2f} Total:${total_item:.2f}"
            )
        subtotal_total = round(subtotal_total, 2)
        iva_total = round(iva_total, 2)
        total_bruto = subtotal_total + iva_total

        descuento_total = getattr(venta, "descuento_total", 0) or 0
        if descuento_total > 0:
            lines.append(f"{'Descuento:':<20} -${descuento_total:.2f}")

        total_final = round(max(0, total_bruto - descuento_total), 2)
        lines.append("-" * self.WIDTH)
        lines.append(f"{'Subtotal:':<20} ${subtotal_total:.2f}")
        lines.append(f"{'IVA 19%:':<20} ${iva_total:.2f}")
        lines.append(f"{'TOTAL:':<20} ${total_final:.2f}")
        lines.append("=" * self.WIDTH)
        lines.append("Gracias por su compra!")
        lines.append("")
        return "\n".join(lines)

    def generar_html(self, venta, items):
        """Genera el ticket en formato HTML para impresión"""
        store_name = get_store_name()
        address = get_address()
        phone = get_phone()
        nit = get_nit()
        email = get_email()

        logo_path = get_logo_path()
        logo_img = ""
        if logo_path and os.path.exists(logo_path):
            logo_img = (
                f'<img src="{logo_path}" width="100" style="margin-bottom: 10px;"><br>'
            )

        items_html = ""
        IVA_RATE = 0.19
        subtotal_total = 0
        iva_total = 0
        for item in items:
            producto = item.producto
            cantidad = item.cantidad
            precio = item.precio
            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2)
            total_item = round(subtotal + iva, 2)
            subtotal_total += subtotal
            iva_total += iva
            items_html += f"""
            <tr>
                <td>{producto.nombre}</td>
                <td style="text-align:center">{cantidad}</td>
                <td style="text-align:right">${precio:.2f}</td>
                <td style="text-align:right">${iva:.2f}</td>
                <td style="text-align:right">${total_item:.2f}</td>
            </tr>
            """
        subtotal_total = round(subtotal_total, 2)
        iva_total = round(iva_total, 2)
        total_final = round(subtotal_total + iva_total, 2)

        metodo_pago = getattr(venta, "metodo_pago", None)
        html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            width: 300px;
            margin: 0 auto;
            color: #2c3e50;
        }}
        .header {{
            text-align: center;
            margin-bottom: 16px;
            padding: 12px 0;
            border-bottom: 2px solid #2c3e50;
        }}
        .store-name {{
            font-size: 20px;
            font-weight: bold;
            color: #1a252f;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .store-type {{
            font-size: 11px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }}
        .info {{
            font-size: 11px;
            color: #555;
            line-height: 1.6;
        }}
        .nit {{
            font-size: 11px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 10px;
        }}
        th {{
            border-bottom: 1px solid #bdc3c7;
            padding: 4px;
            text-align: left;
            font-size: 11px;
            color: #7f8c8d;
        }}
        td {{ padding: 4px; text-align: left; }}
        .total-row {{
            border-top: 2px solid #2c3e50;
            font-weight: bold;
            font-size: 14px;
            margin-top: 8px;
            padding-top: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 16px;
            font-size: 10px;
            color: #95a5a6;
            border-top: 1px solid #ecf0f1;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {logo_img}
        <div class="store-name">{store_name}</div>
        {f'<div class="info">{address}</div>' if address else ""}
        {f'<div class="info">Tel: {phone}</div>' if phone else ""}
        {f'<div class="info">{email}</div>' if email else ""}
        {f'<div class="nit">NIT: {nit}</div>' if nit else ""}
    </div>
    <div class="info">
        Fecha: {venta.fecha.strftime("%d/%m/%Y %I:%M %p")}&nbsp;&nbsp;
        Ticket #: {venta.id}
        {f"<br>Método: {metodo_pago}" if metodo_pago else ""}
    </div>
    <table>
        <thead>
            <tr>
                <th>Producto</th>
                <th>Cant</th>
                <th>Precio</th>
                <th>IVA</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>
    <div class="total-row">
        Subtotal: ${subtotal_total:.2f}<br>
        IVA 19%: ${iva_total:.2f}<br>
        <strong>TOTAL: ${total_final:.2f}</strong>
    </div>
    <div class="footer">
        <p>¡Gracias por su compra!</p>
        <p>{store_name} — {email}</p>
    </div>
</body>
</html>
"""
        return html

    def imprimir(self, venta, items):
        """Imprime el ticket en consola y guarda en PDF diario"""
        ticket = self.generar(venta, items)
        print(ticket)
        try:
            from tucajero.utils.factura_diaria import agregar_ticket_a_pdf_diario

            agregar_ticket_a_pdf_diario(venta, items)
        except Exception as e:
            print(f"[WARN] No se pudo guardar en PDF diario: {e}")
        return ticket

    def imprimir_html(self, venta, items):
        """Genera ticket en HTML para impresión"""
        return self.generar_html(venta, items)


def generar_facturas_dia(fecha=None):
    """
    Genera el PDF de facturas para un día específico.
    Si fecha es None, usa la fecha actual.
    Retorna la ruta del PDF generado.
    """
    from tucajero.utils.factura_diaria import (
        get_factura_diaria_path,
        get_facturas_dir,
        _generar_pdf_diario,
    )
    from tucajero.utils.store_config import (
        get_store_name,
        get_address,
        get_phone,
        get_email,
        get_nit,
    )
    import json
    import os

    if fecha is None:
        from datetime import datetime

        fecha = datetime.now().date()

    json_path = os.path.join(
        get_facturas_dir(), f"facturas_{fecha.strftime('%Y-%m-%d')}_data.json"
    )
    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tickets = json.load(f)
    except Exception:
        return None

    if not tickets:
        return None

    pdf_path = get_factura_diaria_path(fecha)
    _generar_pdf_diario(
        pdf_path,
        tickets,
        get_store_name(),
        get_address(),
        get_phone(),
        get_email(),
        get_nit(),
    )
    return pdf_path
