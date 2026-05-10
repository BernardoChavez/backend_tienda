import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from datetime import datetime

def generar_pdf_cotizacion(carrito, empresa):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_title = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=12,
        alignment=1 # Center
    )
    
    elements = []

    # Encabezado
    elements.append(Paragraph(f"COTIZACIÓN FORMAL", style_title))
    elements.append(Paragraph(f"<b>Empresa:</b> {empresa.nombre}", styles['Normal']))
    elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Cliente:</b> {carrito.usuario.nombre} {carrito.usuario.apellido} ({carrito.usuario.username})", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    # Tabla de Productos
    data = [['Producto', 'SKU', 'Precio Unit.', 'Cant.', 'Subtotal']]
    for detalle in carrito.detalles.all():
        data.append([
            detalle.variante_producto.producto.nombre,
            detalle.variante_producto.sku,
            f"{detalle.variante_producto.precio:.2f}",
            str(detalle.cantidad),
            f"{detalle.subtotal:.2f}"
        ])
    
    # Fila de Total
    data.append(['', '', '', 'TOTAL:', f"BOB {carrito.total:.2f}"])

    table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 0.8*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Alinear nombres a la izquierda
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'), # Total en negrita
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # Términos y condiciones
    elements.append(Paragraph("<b>Términos y Condiciones:</b>", styles['Normal']))
    elements.append(Paragraph("1. Esta cotización tiene una validez de 15 días calendario.", styles['Normal']))
    elements.append(Paragraph("2. Los precios incluyen impuestos de ley.", styles['Normal']))
    elements.append(Paragraph("3. La entrega se coordinará tras la confirmación del pago.", styles['Normal']))
    
    # Estilo centrado para firma
    style_center = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        alignment=1 # Center
    )

    elements.append(Spacer(1, 1 * inch))
    

    doc.build(elements)
    buffer.seek(0)
    return buffer
