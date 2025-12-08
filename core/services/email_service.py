from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


class EmailService:

    def enviar_correo_masivo_con_adjunto(self, destinatarios, asunto, mensaje, archivo=None):
        try:
            email = EmailMessage(
                subject=asunto,
                body=mensaje,
                from_email=settings.EMAIL_HOST_USER,
                to=destinatarios
            )

            # Adjuntar archivo si existe
            if archivo:
                email.attach(archivo.name, archivo.read(), archivo.content_type)

            email.send()

        except Exception as e:
            print("Error en EmailService:", e)
            raise e


class ReceiptEmailService:
    """Servicio para enviar comprobantes de pago por correo."""

    @staticmethod
    def enviar_comprobante(venta, persona, productos_para_email, request=None):
        try:
            # Obtener email del cliente
            email_cliente = getattr(persona, 'correo_persona', None)
            if not email_cliente:
                print("No se pudo enviar comprobante: cliente sin email")
                return False

            # Datos básicos
            nombre_cliente = f"{getattr(persona, 'nombre_persona','')} {getattr(persona, 'apellido_persona','')}".strip() or "Cliente"
            numero_pedido = f"ART-000{getattr(venta, 'id_venta', 'N/A')}"
            total_venta = float(getattr(venta, 'total', 0) or 0)
            fecha_venta = getattr(venta, 'fecha_venta', None)
            metodo_pago = getattr(venta, 'metodo_pago', "Transferencia Bancaria") or "Transferencia Bancaria"
            direccion_envio = getattr(venta, 'direccion_envio', "") or ""

            # Subtotal y descuento
            subtotal = sum(float(p.get('subtotal', 0) or 0) for p in productos_para_email)
            descuento = float(getattr(venta, 'descuento', 0) or 0)

            # Contexto
            contexto = {
                'nombre_cliente': nombre_cliente,
                'numero_pedido': numero_pedido,
                'fecha_venta': fecha_venta,
                'metodo_pago': metodo_pago,
                'email_cliente': email_cliente,
                'direccion_envio': direccion_envio,
                'email_soporte': settings.DEFAULT_FROM_EMAIL,
                'productos': productos_para_email or [],
                'subtotal': float(subtotal),
                'descuento': float(descuento),
                'total': float(total_venta),
            }

            print("Contexto del email:", contexto)

            html_content = render_to_string('emails/payment_receipt.html', contexto)

            asunto = f"Comprobante de Pago - Orden {numero_pedido} - Artesano Market"
            texto_plano = f"""
Comprobante de Pago - {numero_pedido}

Hola {nombre_cliente},

Gracias por tu compra en Artesano Market.

Número de Pedido: {numero_pedido}
Total Pagado: ${total_venta:,.0f} COP

Este es un comprobante generado automáticamente.
Para ver todos los detalles, abre este correo con un cliente que soporte HTML.

Gracias,
Artesano Market
"""

            email = EmailMultiAlternatives(
                subject=asunto,
                body=texto_plano,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_cliente]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Comprobante enviado exitosamente a {email_cliente}")
            return True

        except Exception as e:
            print(f"Error en ReceiptEmailService.enviar_comprobante: {e}")
            import traceback; traceback.print_exc()
            return False


class ShipmentEmailService:
    """Servicio para enviar comprobantes de envío por correo."""

    @staticmethod
    def enviar_comprobante_envio(venta, persona, productos_para_email, vendedor_persona, request=None):
        try:
            email_cliente = getattr(persona, 'correo_persona', None)
            if not email_cliente:
                print("No se pudo enviar comprobante de envío: cliente sin email")
                return False

            nombre_cliente = f"{getattr(persona, 'nombre_persona','')} {getattr(persona, 'apellido_persona','')}".strip() or "Cliente"
            numero_pedido = f"ART-000{getattr(venta, 'id_venta', 'N/A')}"
            nombre_vendedor = f"{getattr(vendedor_persona, 'nombre_persona','')} {getattr(vendedor_persona, 'apellido_persona','')}".strip() or "Vendedor"
            fecha_envio = getattr(venta, 'fecha_venta', None)
            direccion_envio = getattr(venta, 'direccion_envio', "") or ""

            contexto = {
                'nombre_cliente': nombre_cliente,
                'numero_pedido': numero_pedido,
                'fecha_envio': fecha_envio,
                'nombre_vendedor': nombre_vendedor,
                'email_cliente': email_cliente,
                'direccion_envio': direccion_envio,
                'email_soporte': settings.DEFAULT_FROM_EMAIL,
                'productos': productos_para_email or [],
            }

            print("Contexto del email de envío:", contexto)

            html_content = render_to_string('emails/shipment_receipt.html', contexto)

            asunto = f"Comprobante de Envío - Orden {numero_pedido} - Artesano Market"
            texto_plano = f"""
Comprobante de Envío - {numero_pedido}

Hola {nombre_cliente},

Tu pedido ha sido marcado como enviado por {nombre_vendedor}.

Número de Pedido: {numero_pedido}
Estado: Enviado

Este es un comprobante generado automáticamente.
Para ver todos los detalles, abre este correo con un cliente que soporte HTML.

Gracias,
Artesano Market
"""

            email = EmailMultiAlternatives(
                subject=asunto,
                body=texto_plano,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_cliente]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Comprobante de envío enviado exitosamente a {email_cliente}")
            return True

        except Exception as e:
            print(f"Error en ShipmentEmailService.enviar_comprobante_envio: {e}")
            import traceback; traceback.print_exc()
            return False
