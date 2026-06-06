"""
skills/itinerario_pdf.py — Skill: Generador de itinerario en PDF
Cuando el usuario pide un plan de viaje, esta skill genera un PDF
descargable con el itinerario sugerido por el asistente.
"""

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


# Colores temáticos del Eje Cafetero
VERDE_CAFE   = colors.HexColor("#2D6A4F")
CAFE_OSCURO  = colors.HexColor("#4A2C0A")
CREMA        = colors.HexColor("#F5F0E8")


def generar_itinerario_pdf(pregunta: str, respuesta: str) -> bytes:
    """
    Genera un PDF con el itinerario turístico.

    Args:
        pregunta: Pregunta original del usuario.
        respuesta: Respuesta generada por el Agente Redactor.

    Returns:
        Bytes del PDF generado (para descarga directa en Streamlit).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    estilos = getSampleStyleSheet()

    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        fontSize=22,
        textColor=VERDE_CAFE,
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontSize=12,
        textColor=CAFE_OSCURO,
        spaceAfter=16,
    )
    estilo_cuerpo = ParagraphStyle(
        "Cuerpo",
        parent=estilos["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )
    estilo_pie = ParagraphStyle(
        "Pie",
        parent=estilos["Normal"],
        fontSize=9,
        textColor=colors.grey,
    )

    # Contenido del PDF
    elementos = [
        Paragraph("🌿 Itinerario Turístico", estilo_titulo),
        Paragraph("Eje Cafetero — Colombia", estilo_subtitulo),
        HRFlowable(width="100%", thickness=1, color=VERDE_CAFE),
        Spacer(1, 0.4 * cm),
        Paragraph(f"<b>Tu consulta:</b> {pregunta}", estilo_cuerpo),
        Spacer(1, 0.3 * cm),
        Paragraph("<b>Plan sugerido:</b>", estilo_cuerpo),
    ]

    # Convertir el markdown de la respuesta a párrafos del PDF
    for linea in respuesta.split("\n"):
        linea = linea.strip()
        if not linea:
            elementos.append(Spacer(1, 0.2 * cm))
        elif linea.startswith("##"):
            elementos.append(Paragraph(linea.replace("##", "").strip(), estilo_subtitulo))
        elif linea.startswith("#"):
            elementos.append(Paragraph(linea.replace("#", "").strip(), estilo_titulo))
        elif linea.startswith("- ") or linea.startswith("* "):
            elementos.append(Paragraph(f"• {linea[2:]}", estilo_cuerpo))
        else:
            elementos.append(Paragraph(linea, estilo_cuerpo))

    # Pie de página
    elementos.extend([
        Spacer(1, 0.8 * cm),
        HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey),
        Spacer(1, 0.2 * cm),
        Paragraph(
            f"Generado por el Asistente Turístico del Eje Cafetero · {date.today().strftime('%d/%m/%Y')}",
            estilo_pie,
        ),
        Paragraph(
            "Este itinerario es una sugerencia basada en información turística pública.",
            estilo_pie,
        ),
    ])

    doc.build(elementos)
    return buffer.getvalue()
