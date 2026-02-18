from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import zipfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from datetime import datetime
import os
import uuid
from reportlab.platypus import Image


router = APIRouter(prefix="/liquidacion", tags=["Liquidación"])

DEPOSITO_CONDUCTOR = 150


# =====================================================
# LOGO SUPERIOR DERECHO (JPG)
# =====================================================
def agregar_marca_de_agua(canvas_obj, doc):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.abspath(
        os.path.join(BASE_DIR, "..", "static", "logo_mexicargo.png")
    )

    if os.path.exists(logo_path):
        canvas_obj.saveState()
        # Establecer transparencia (0.1 es muy tenue, 0.2 es moderada)
        canvas_obj.setFillAlpha(0.15) 
        
        width, height = doc.pagesize
        img_width = 400  # Ajusta el tamaño de la marca de agua
        img_height = 200 # Ajusta según la proporción de tu logo
        
        # Dibujar en el centro de la página
        canvas_obj.drawImage(
            logo_path,
            (width - img_width) / 2,
            (height - img_height) / 2 + 40,
            width=img_width,
            height=img_height,
            preserveAspectRatio=True,
            mask='auto'
        )
        canvas_obj.restoreState()


# =====================================================
# ENDPOINT
# =====================================================
@router.post("/procesar")
async def procesar_liquidacion(file: UploadFile = File(...)):

    df = pd.read_excel(file.file)

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:

        for _, row in df.iterrows():

            nombre = row.get("Nombre", "")
            cargo = row.get("Cargo", "")
            horas_raw = row.get("Horas", 0)

            # =========================
            # HORAS
            # =========================
            if isinstance(horas_raw, pd.Timedelta):
                horas = horas_raw.total_seconds() / 3600
            elif isinstance(horas_raw, str) and ":" in horas_raw:
                h, m, s = map(int, horas_raw.split(":"))
                horas = h + m / 60 + s / 3600
            else:
                horas = float(horas_raw)

            # =========================
            # VALOR HORA
            # =========================
            valor_hora = float(row.get("ValorHora", 0))

            # =========================
            # DESCUENTO
            # =========================
            descuento_raw = row.get("Descuento", 0)
            descuento = 0 if pd.isna(descuento_raw) else float(descuento_raw)

            # =========================
            # FECHAS
            # =========================
            fecha_inicio = pd.to_datetime(row.get("FechaInicio")).strftime("%m/%d/%Y")
            fecha_fin = pd.to_datetime(row.get("FechaFin")).strftime("%m/%d/%Y")

            # =========================
            # CÁLCULOS
            # =========================
            total = horas * valor_hora

            if str(cargo).strip().upper() == "CONDUCTOR":
                deposito = DEPOSITO_CONDUCTOR
            else:
                deposito = 0

            neto = total - descuento - deposito

            # =========================
            # NUMERO RECIBO AUTOMÁTICO
            # =========================
            numero_recibo = f"MX-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:5].upper()}"

            # =========================
            # PDF
            # =========================
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=pagesizes.A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=60,
                bottomMargin=40
            )

            elements = []
            styles = getSampleStyleSheet()

            # Título
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.abspath(
                os.path.join(BASE_DIR, "..", "static", "logo_mexicargo.png")
            )

            if os.path.exists(logo_path):
                logo = Image(logo_path)
                logo.drawHeight = 60
                logo.drawWidth = 180
                logo.hAlign = "RIGHT"
                elements.append(logo)

            elements.append(Spacer(1, 10))
            elements.append(Paragraph("<b>FACTURA DE NÓMINA</b>", styles["Title"]))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("<b>Mexicargo</b>", styles["Title"]))
            elements.append(Spacer(1, 15))

            elements.append(Paragraph(f"<b>No. Recibo:</b> {numero_recibo}", styles["Normal"]))
            elements.append(Spacer(1, 15))

            # Datos empleado
            elements.append(Paragraph(f"<b>Nombre:</b> {nombre}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Cargo:</b> {cargo}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Valor por Hora:</b> ${valor_hora:,.2f}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Fecha Inicio:</b> {fecha_inicio}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Fecha Fin:</b> {fecha_fin}", styles["Normal"]))

            elements.append(Spacer(1, 25))

            # Tabla financiera
            data = [
                ["Concepto", "Monto"],
                ["Horas Trabajadas", f"{horas:.2f}"],
                ["Total A Pagar", f"${total:,.2f}"],
                ["Depósito Directo", f"${deposito:,.2f}"],
                ["Descuento", f"${descuento:,.2f}"],
                ["Valor Neto a Pagar", f"${neto:,.2f}"],
            ]

            table = Table(data, colWidths=[3.5 * inch, 2 * inch])

            table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6E2E")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCE6DC")),
                ])
            )

            elements.append(table)
            elements.append(Spacer(1, 60))
            elements.append(Paragraph("Recibí Conforme _________________________________", styles["Normal"]))
            
            doc.build(elements, onFirstPage=agregar_marca_de_agua, onLaterPages=agregar_marca_de_agua)

            pdf_buffer.seek(0)

            filename = f"{str(nombre).replace(' ', '_')}.pdf"
            zip_file.writestr(filename, pdf_buffer.read())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=Recibos_Liquidacion.zip"},
    )
