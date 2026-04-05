"""
Utilidad para enviar tickets por email
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from tucajero.utils.store_config import get_store_name, get_email
from tucajero.utils.ticket import GeneradorTicket


def enviar_ticket_email(destinatario, venta, items, html=True):
    """
    Envía el ticket de una venta al email del cliente.

    Args:
        destinatario: Email del destinatario
        venta: Objeto Venta
        items: Lista de VentaItem
        html: Si True, envía en formato HTML; si False, texto plano

    Returns:
        tuple: (success: bool, message: str)
    """
    store_name = get_store_name()
    remitente = get_email()

    if not remitente:
        return False, "No hay email del negocio configurado en Configuración."

    if not destinatario or "@" not in destinatario:
        return False, "Email del destinatario no válido."

    # Obtener configuración de SMTP desde variables de entorno
    smtp_host = os.environ.get("TUCAJERO_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("TUCAJERO_SMTP_PORT", "587"))
    smtp_user = os.environ.get("TUCAJERO_SMTP_USER", remitente)
    smtp_password = os.environ.get("TUCAJERO_SMTP_PASSWORD", "")

    if not smtp_password:
        return False, (
            "No hay contraseña SMTP configurada.\n\n"
            "Configure las variables de entorno:\n"
            "  TUCAJERO_SMTP_PASSWORD=contraseña\n"
            "  TUCAJERO_SMTP_HOST=smtp.gmail.com (opcional)\n"
            "  TUCAJERO_SMTP_PORT=587 (opcional)"
        )

    generador = GeneradorTicket()

    # Crear mensaje
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{store_name} <{remitente}>"
    msg["To"] = destinatario
    msg["Subject"] = f"Ticket #{venta.id} - {store_name}"

    # Cuerpo en texto plano
    ticket_text = generador.generar(venta, items)
    parte_texto = MIMEText(ticket_text, "plain", "utf-8")
    msg.attach(parte_texto)

    # Cuerpo en HTML (opcional)
    if html:
        ticket_html = generador.generar_html(venta, items)
        parte_html = MIMEText(ticket_html, "html", "utf-8")
        msg.attach(parte_html)

    # Enviar
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True, f"Ticket #{venta.id} enviado a {destinatario}"
    except smtplib.SMTPAuthenticationError:
        return False, (
            "Error de autenticación SMTP.\n"
            "Verifique la contraseña en TUCAJERO_SMTP_PASSWORD.\n"
            "Para Gmail, use una 'Contraseña de aplicación'."
        )
    except smtplib.SMTPException as e:
        return False, f"Error SMTP: {str(e)}"
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"
