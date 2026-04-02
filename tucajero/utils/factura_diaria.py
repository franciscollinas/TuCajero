import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def get_facturas_dir():
    """Retorna el directorio de facturas diarias"""
    from tucajero.config.database import get_data_dir

    facturas_dir = os.path.join(get_data_dir(), "facturas")
    os.makedirs(facturas_dir, exist_ok=True)
    return facturas_dir


def get_factura_diaria_path(fecha=None):
    """Retorna la ruta del PDF del día"""
    if fecha is None:
        fecha = datetime.now().date()
    facturas_dir = get_facturas_dir()
    nombre = f"facturas_{fecha.strftime('%Y-%m-%d')}.pdf"
    return os.path.join(facturas_dir, nombre)


def agregar_ticket_a_pdf_diario(venta, items):
    """
    Agrega el ticket de una venta al PDF diario acumulativo.
    Si el PDF del día no existe lo crea.
    Si ya existe agrega la nueva factura al final.
    """
    from tucajero.utils.store_config import (
        get_store_name,
        get_address,
        get_phone,
        get_email,
        get_nit,
    )

    pdf_path = get_factura_diaria_path()

    tickets_existentes = []
    if os.path.exists(pdf_path):
        try:
            import json

            json_path = pdf_path.replace(".pdf", "_data.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    tickets_existentes = json.load(f)
        except Exception:
            tickets_existentes = []

    ticket_data = {
        "venta_id": venta.id,
        "fecha": venta.fecha.strftime("%d/%m/%Y %I:%M:%S %p"),
        "total": venta.total,
        "metodo_pago": getattr(venta, "metodo_pago", "efectivo") or "efectivo",
        "items": [
            {
                "nombre": item.producto.nombre,
                "cantidad": item.cantidad,
                "precio": item.precio,
                "subtotal": item.cantidad * item.precio,
            }
            for item in items
        ],
    }
    tickets_existentes.append(ticket_data)

    import json

    json_path = pdf_path.replace(".pdf", "_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tickets_existentes, f, ensure_ascii=False, indent=2)

    _generar_pdf_diario(
        pdf_path,
        tickets_existentes,
        get_store_name(),
        get_address(),
        get_phone(),
        get_email(),
        get_nit(),
    )

    return pdf_path


def _generar_pdf_diario(pdf_path, tickets, store_name, address, phone, email, nit):
    """Genera el PDF con todos los tickets del día"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontSize=16,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )
    style_ticket_header = ParagraphStyle(
        "TicketHeader",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        spaceAfter=4,
        spaceBefore=12,
    )
    style_normal = ParagraphStyle(
        "Normal2",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        spaceAfter=2,
    )

    story = []

    story.append(Paragraph(store_name.upper(), style_titulo))
    if address:
        story.append(Paragraph(address, style_subtitulo))
    if phone:
        story.append(Paragraph(f"Tel: {phone}", style_subtitulo))
    if email:
        story.append(Paragraph(email, style_subtitulo))
    if nit:
        story.append(Paragraph(f"NIT: {nit}", style_subtitulo))

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"FACTURAS DEL DÍA — {fecha_hoy}  |  Total ventas: {len(tickets)}",
            ParagraphStyle(
                "dia",
                parent=styles["Normal"],
                fontSize=10,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2c3e50"),
            ),
        )
    )
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c3e50"))
    )
    story.append(Spacer(1, 0.3 * cm))

    metodos_label = {
        "efectivo": "Efectivo",
        "nequi": "Nequi",
        "daviplata": "Daviplata",
        "transferencia": "Transferencia",
        "mixto": "Mixto",
    }

    for ticket in tickets:
        story.append(
            Paragraph(
                f"Ticket #{ticket['venta_id']}  —  {ticket['fecha']}  —  "
                f"Método: {metodos_label.get(ticket['metodo_pago'], ticket['metodo_pago'])}",
                style_ticket_header,
            )
        )

        data = [["Producto", "Cant.", "Precio unit.", "Subtotal"]]
        for item in ticket["items"]:
            data.append(
                [
                    item["nombre"],
                    str(item["cantidad"]),
                    f"${item['precio']:,.2f}",
                    f"${item['subtotal']:,.2f}",
                ]
            )

        tabla = Table(data, colWidths=[9 * cm, 2 * cm, 3 * cm, 3 * cm])
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8f9fa")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tabla)

        total_data = [["", "", "TOTAL:", f"${ticket['total']:,.2f}"]]
        total_tabla = Table(total_data, colWidths=[9 * cm, 2 * cm, 3 * cm, 3 * cm])
        total_tabla.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEABOVE", (2, 0), (-1, -1), 1, colors.HexColor("#2c3e50")),
                ]
            )
        )
        story.append(total_tabla)
        story.append(
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6"))
        )

    if tickets:
        story.append(Spacer(1, 0.5 * cm))
        total_dia = sum(t["total"] for t in tickets)
        story.append(
            HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c3e50"))
        )
        story.append(
            Paragraph(
                f"TOTAL DEL DÍA: ${total_dia:,.2f}  |  "
                f"Ventas registradas: {len(tickets)}",
                ParagraphStyle(
                    "resumen",
                    parent=styles["Normal"],
                    fontSize=12,
                    fontName="Helvetica-Bold",
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#27ae60"),
                    spaceBefore=8,
                ),
            )
        )

    doc.build(story)


def limpiar_datos_dia_anterior():
    """Elimina el JSON auxiliar de días anteriores (limpieza opcional)"""
    import json
    from datetime import date, timedelta

    ayer = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    json_path = os.path.join(get_facturas_dir(), f"facturas_{ayer}_data.json")
    if os.path.exists(json_path):
        try:
            os.remove(json_path)
        except Exception:
            pass
