import matplotlib
matplotlib.use('Agg')
import io
from django.http import FileResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.conf import settings
import matplotlib.pyplot as plt

from core.models import Productos, Vendedores, Personas

# ============================================
#   FUNCIÓN PARA AGREGAR ENCABEZADO EN PDF
# ============================================
def encabezado(canva, doc):
    canva.saveState()

    # 🔽 BAJADO para que no quede pegado al borde
    top_margin = 750  

    # Ruta del logo
    logo_path = settings.BASE_DIR / "core/static/images/logo_artesano.png"

    # Logo
    try:
        canva.drawImage(
            str(logo_path),
            40,                 # X
            top_margin - 40,    # Y
            width=60,
            height=60,
            preserveAspectRatio=True,
            mask='auto'
        )
    except:
        pass

    # Título
    canva.setFont("Helvetica-Bold", 22)
    canva.drawCentredString(300, top_margin - 25, "Artesano Market")

    # Línea inferior
    canva.setLineWidth(1)
    canva.line(30, top_margin - 40, 580, top_margin - 40)

    canva.restoreState()


# ====================================================
#             FUNCIÓN PRINCIPAL DEL REPORTE
# ====================================================
def generar_reporte_productos_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=120  # 🔽 aumenté un poco el margen para evitar choques
    )

    styles = getSampleStyleSheet()
    elementos = []

    # Título del reporte
    elementos.append(Paragraph("Reporte de Productos", styles["Title"]))
    elementos.append(Spacer(1, 12))

    # Obtener el vendedor del usuario autenticado
    user_id = request.session.get("user_id")
    if not user_id:
        return FileResponse(buffer, as_attachment=True, filename="reporte_productos.pdf")
    
    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        return FileResponse(buffer, as_attachment=True, filename="reporte_productos.pdf")
    
    vendedor = Vendedores.objects.filter(personas_id_personas=persona.id_personas).first()
    if not vendedor:
        return FileResponse(buffer, as_attachment=True, filename="reporte_productos.pdf")

    productos = Productos.objects.filter(vendedor=vendedor)

    # Tabla
    data = [["Nombre", "Precio", "Stock"]]
    for p in productos:
        data.append([p.nombre, f"${p.precio}", p.cantidad_existente])

    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 25))

    # =======================
    #   GRÁFICA DE BARRAS
    # =======================
    nombres = [p.nombre for p in productos]
    stocks = [p.cantidad_existente for p in productos]

    plt.figure()
    plt.bar(nombres, stocks)
    plt.xticks(rotation=45)
    plt.title("Stock por Producto")

    bar_buffer = io.BytesIO()
    plt.savefig(bar_buffer, format='png', bbox_inches='tight')
    plt.close()

    bar_buffer.seek(0)
    elementos.append(Image(bar_buffer, width=400, height=250))
    elementos.append(Spacer(1, 25))

    # =======================
    #   GRÁFICA CIRCULAR
    # =======================
    plt.figure()
    plt.pie(stocks, labels=nombres, autopct="%1.1f%%")
    plt.title("Distribución de Stock")

    pie_buffer = io.BytesIO()
    plt.savefig(pie_buffer, format='png', bbox_inches='tight')
    plt.close()

    pie_buffer.seek(0)
    elementos.append(Image(pie_buffer, width=400, height=250))
    elementos.append(Spacer(1, 25))

    # Generar PDF con encabezado
    doc.build(
        elementos,
        onFirstPage=encabezado,
        onLaterPages=encabezado
    )

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="reporte_productos.pdf")
