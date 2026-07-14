from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from docx import Document
from docx.shared import Inches
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from pydantic import BaseModel, Field

from ml.predictor import FinancialRiskPredictor
from ml.schema import DEFAULT_SAMPLE, FEATURE_COLUMNS
from ml.statistical_validation import statistical_validation_summary


class PredictionRequest(BaseModel):
    LIMIT_BAL: float = Field(..., ge=1, description="Monto de credito concedido")
    SEX: int = Field(2, ge=1, le=2)
    EDUCATION: int = Field(2, ge=1, le=4)
    MARRIAGE: int = Field(1, ge=1, le=3)
    AGE: int = Field(..., ge=18, le=100)
    PAY_0: int = 0
    PAY_2: int = 0
    PAY_3: int = 0
    PAY_4: int = 0
    PAY_5: int = 0
    PAY_6: int = 0
    BILL_AMT1: float = 0
    BILL_AMT2: float = 0
    BILL_AMT3: float = 0
    BILL_AMT4: float = 0
    BILL_AMT5: float = 0
    BILL_AMT6: float = 0
    PAY_AMT1: float = 0
    PAY_AMT2: float = 0
    PAY_AMT3: float = 0
    PAY_AMT4: float = 0
    PAY_AMT5: float = 0
    PAY_AMT6: float = 0


class PredictionResponse(BaseModel):
    probability: float
    risk_label: str
    mode: str
    threshold: float
    prediction: int
    explanation: List[str]
    model_name: str


class ChatbotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=600)
    language: str = Field("es", pattern="^(es|en)$")


class ChatbotResponse(BaseModel):
    answer: str
    language: str
    topics: List[str]


app = FastAPI(
    title="Asesor Financiero Personal IA API",
    description="API para prediccion de riesgo financiero con modelos de redes neuronales.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = FinancialRiskPredictor()


MONEY_FIELDS = [
    "LIMIT_BAL",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
]

FIELD_LABELS = {
    "LIMIT_BAL": "Credito concedido",
    "SEX": "Sexo",
    "EDUCATION": "Educacion",
    "MARRIAGE": "Estado civil",
    "AGE": "Edad",
    "PAY_0": "Mora mes actual",
    "PAY_2": "Mora mes -2",
    "PAY_3": "Mora mes -3",
    "PAY_4": "Mora mes -4",
    "PAY_5": "Mora mes -5",
    "PAY_6": "Mora mes -6",
    "BILL_AMT1": "Saldo 1",
    "BILL_AMT2": "Saldo 2",
    "BILL_AMT3": "Saldo 3",
    "BILL_AMT4": "Saldo 4",
    "BILL_AMT5": "Saldo 5",
    "BILL_AMT6": "Saldo 6",
    "PAY_AMT1": "Pago 1",
    "PAY_AMT2": "Pago 2",
    "PAY_AMT3": "Pago 3",
    "PAY_AMT4": "Pago 4",
    "PAY_AMT5": "Pago 5",
    "PAY_AMT6": "Pago 6",
}

SEX_LABELS = {1: "Masculino", 2: "Femenino"}
EDUCATION_LABELS = {1: "Posgrado", 2: "Universidad", 3: "Secundaria", 4: "Otros"}
MARRIAGE_LABELS = {1: "Casado", 2: "Soltero", 3: "Otros"}


def money(value: float) -> str:
    return f"S/ {float(value):,.0f}".replace(",", " ")


def percent(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def display_value(key: str, value: float) -> str:
    if key in MONEY_FIELDS:
        return money(value)
    if key == "SEX":
        return SEX_LABELS.get(int(value), str(value))
    if key == "EDUCATION":
        return EDUCATION_LABELS.get(int(value), str(value))
    if key == "MARRIAGE":
        return MARRIAGE_LABELS.get(int(value), str(value))
    return str(int(value)) if float(value).is_integer() else str(value)


def financial_indicators(payload: Dict) -> Dict[str, float]:
    bills = [max(float(payload.get(f"BILL_AMT{i}", 0)), 0.0) for i in range(1, 7)]
    payments = [max(float(payload.get(f"PAY_AMT{i}", 0)), 0.0) for i in range(1, 7)]
    delays = [float(payload.get(key, 0)) for key in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]]
    total_bills = sum(bills)
    total_payments = sum(payments)
    limit_bal = max(float(payload.get("LIMIT_BAL", 1)), 1.0)
    return {
        "total_bills": total_bills,
        "total_payments": total_payments,
        "credit_usage": min(total_bills / (limit_bal * 6.0), 2.0),
        "payment_coverage": total_payments / max(total_bills, 1.0),
        "max_delay": max(delays),
        "average_bill": total_bills / 6.0,
        "average_payment": total_payments / 6.0,
    }


def recommendations(result: Dict, indicators: Dict) -> List[str]:
    probability = float(result["probability"])
    notes = []
    if probability >= 0.70:
        notes.append("Revisar la capacidad de pago antes de aprobar nuevas obligaciones.")
        notes.append("Priorizar reduccion de mora y pagos minimos por encima de nuevos consumos.")
    elif probability >= 0.40:
        notes.append("Mantener seguimiento mensual del saldo y evitar crecimiento de deuda.")
        notes.append("Aumentar pagos para mejorar la cobertura frente al saldo facturado.")
    else:
        notes.append("Mantener el comportamiento actual y conservar pagos puntuales.")
        notes.append("Usar el credito de forma moderada para sostener un perfil saludable.")
    if indicators["credit_usage"] > 0.75:
        notes.append("La utilizacion promedio del credito es elevada; conviene reducir saldos.")
    if indicators["payment_coverage"] < 0.10:
        notes.append("La cobertura de pagos es baja frente al saldo total; revisar presupuesto mensual.")
    if indicators["max_delay"] > 0:
        notes.append("Existe mora historica; corregir atrasos mejora la clasificacion de riesgo.")
    return notes


def report_context(request: PredictionRequest) -> Dict:
    payload = request.model_dump()
    result = predictor.predict(payload)
    indicators = financial_indicators(payload)
    return {
        "payload": payload,
        "result": result,
        "indicators": indicators,
        "recommendations": recommendations(result, indicators),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def build_pdf_report(context: Dict) -> bytes:
    payload = context["payload"]
    result = context["result"]
    indicators = context["indicators"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 9, "Reporte financiero del programa", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 7, f"Generado: {context['generated_at']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 7, f"Modelo: {result['model_name']} | modo: {result['mode']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 8, "Resultado del analisis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 7, f"Probabilidad de incumplimiento: {percent(result['probability'])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 7, f"Nivel de riesgo: {result['risk_label'].upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 7, f"Decision del umbral: {'incumplimiento probable' if result['prediction'] else 'sin incumplimiento probable'}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 8, "Indicadores financieros", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 10)
    rows = [
        ("Saldos totales", money(indicators["total_bills"])),
        ("Pagos totales", money(indicators["total_payments"])),
        ("Uso promedio de credito", percent(indicators["credit_usage"])),
        ("Cobertura pago / saldo", percent(indicators["payment_coverage"])),
        ("Mora maxima", f"{int(indicators['max_delay'])} meses" if indicators["max_delay"] > 0 else "Sin mora"),
    ]
    for label, value in rows:
        pdf.cell(70, 7, label)
        pdf.cell(0, 7, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 8, "Recomendaciones", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 10)
    for item in context["recommendations"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, f"- {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 8, "Datos ingresados", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 9)
    for key in FEATURE_COLUMNS:
        pdf.cell(62, 6, FIELD_LABELS.get(key, key))
        pdf.cell(0, 6, display_value(key, payload[key]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    return bytes(pdf.output(dest="S"))


def build_docx_report(context: Dict) -> bytes:
    payload = context["payload"]
    result = context["result"]
    indicators = context["indicators"]

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    doc.add_heading("Reporte financiero del programa", level=1)
    doc.add_paragraph(f"Generado: {context['generated_at']}")
    doc.add_paragraph(f"Modelo: {result['model_name']} | modo: {result['mode']}")

    doc.add_heading("Resultado del analisis", level=2)
    table = doc.add_table(rows=4, cols=2)
    table.style = "Table Grid"
    rows = [
        ("Probabilidad de incumplimiento", percent(result["probability"])),
        ("Nivel de riesgo", result["risk_label"].upper()),
        ("Umbral", percent(result["threshold"])),
        ("Decision", "incumplimiento probable" if result["prediction"] else "sin incumplimiento probable"),
    ]
    for index, (label, value) in enumerate(rows):
        table.cell(index, 0).text = label
        table.cell(index, 1).text = value

    doc.add_heading("Indicadores financieros", level=2)
    indicator_table = doc.add_table(rows=1, cols=2)
    indicator_table.style = "Table Grid"
    indicator_table.rows[0].cells[0].text = "Indicador"
    indicator_table.rows[0].cells[1].text = "Valor"
    for label, value in [
        ("Saldos totales", money(indicators["total_bills"])),
        ("Pagos totales", money(indicators["total_payments"])),
        ("Uso promedio de credito", percent(indicators["credit_usage"])),
        ("Cobertura pago / saldo", percent(indicators["payment_coverage"])),
        ("Mora maxima", f"{int(indicators['max_delay'])} meses" if indicators["max_delay"] > 0 else "Sin mora"),
    ]:
        cells = indicator_table.add_row().cells
        cells[0].text = label
        cells[1].text = value

    doc.add_heading("Recomendaciones", level=2)
    for item in context["recommendations"]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("Datos ingresados", level=2)
    data_table = doc.add_table(rows=1, cols=2)
    data_table.style = "Table Grid"
    data_table.rows[0].cells[0].text = "Variable"
    data_table.rows[0].cells[1].text = "Valor"
    for key in FEATURE_COLUMNS:
        cells = data_table.add_row().cells
        cells[0].text = FIELD_LABELS.get(key, key)
        cells[1].text = display_value(key, payload[key])

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def build_xlsx_report(context: Dict) -> bytes:
    payload = context["payload"]
    result = context["result"]
    indicators = context["indicators"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    header_fill = PatternFill("solid", fgColor="E8EEF5")
    bold = Font(bold=True)
    ws.append(["Reporte financiero del programa", context["generated_at"]])
    ws.append(["Modelo", result["model_name"], "Modo", result["mode"]])
    ws.append([])
    ws.append(["Resultado", "Valor"])
    for cell in ws[4]:
        cell.font = bold
        cell.fill = header_fill
    for row in [
        ("Probabilidad de incumplimiento", percent(result["probability"])),
        ("Nivel de riesgo", result["risk_label"].upper()),
        ("Umbral", percent(result["threshold"])),
        ("Decision", "incumplimiento probable" if result["prediction"] else "sin incumplimiento probable"),
    ]:
        ws.append(row)

    ws.append([])
    ws.append(["Indicador", "Valor"])
    for cell in ws[10]:
        cell.font = bold
        cell.fill = header_fill
    for row in [
        ("Saldos totales", money(indicators["total_bills"])),
        ("Pagos totales", money(indicators["total_payments"])),
        ("Uso promedio de credito", percent(indicators["credit_usage"])),
        ("Cobertura pago / saldo", percent(indicators["payment_coverage"])),
        ("Mora maxima", f"{int(indicators['max_delay'])} meses" if indicators["max_delay"] > 0 else "Sin mora"),
    ]:
        ws.append(row)

    ws.append([])
    ws.append(["Recomendaciones"])
    ws[17][0].font = bold
    ws[17][0].fill = header_fill
    for item in context["recommendations"]:
        ws.append([item])

    data_ws = wb.create_sheet("Datos ingresados")
    data_ws.append(["Variable", "Valor"])
    for cell in data_ws[1]:
        cell.font = bold
        cell.fill = header_fill
    for key in FEATURE_COLUMNS:
        data_ws.append([FIELD_LABELS.get(key, key), display_value(key, payload[key])])

    for sheet in [ws, data_ws]:
        sheet.column_dimensions["A"].width = 34
        sheet.column_dimensions["B"].width = 28
        sheet.column_dimensions["C"].width = 18
        sheet.column_dimensions["D"].width = 18

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def report_response(content: bytes, filename: str, media_type: str, inline: bool = False) -> Response:
    disposition = "inline" if inline else "attachment"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
    )


def chatbot_answer(message: str, language: str) -> Dict:
    text = message.lower()
    stats = statistical_validation_summary()
    topics: List[str] = []

    if any(word in text for word in ["modelo", "model", "lstm", "red", "neural"]):
        topics.append("models")
        if language == "en":
            answer = (
                "The program uses LSTM in production because it was selected as the best saved model "
                "after comparing 3 classic neural models (MLP, LSTM, GRU) and 2 hybrid models "
                "(CNN-LSTM and LSTM-Attention). The selection criterion is mainly cross-validation AUC-ROC."
            )
        else:
            answer = (
                "El programa usa LSTM en produccion porque fue seleccionado como el mejor modelo guardado "
                "tras comparar 3 modelos clasicos de redes neuronales (MLP, LSTM, GRU) y 2 modelos hibridos "
                "(CNN-LSTM y LSTM-Attention). El criterio principal es AUC-ROC en validacion cruzada."
            )
    elif any(word in text for word in ["estad", "stat", "wilcoxon", "t-test", "valid"]):
        topics.append("statistics")
        tests = stats.get("statistical_tests", [])
        if language == "en":
            answer = (
                f"The statistical validation module reads {len(tests)} paired comparisons. "
                "It uses paired t-test and Wilcoxon over fold AUC values to verify whether model differences "
                "are robust at the 5% significance level."
            )
        else:
            answer = (
                f"El modulo de pruebas estadisticas lee {len(tests)} comparaciones pareadas. "
                "Usa t-test pareado y Wilcoxon sobre el AUC por fold para validar si las diferencias "
                "entre modelos son robustas al 5% de significancia."
            )
    elif any(word in text for word in ["reporte", "report", "pdf", "word", "excel"]):
        topics.append("reports")
        answer = (
            "You can generate PDF, Word and Excel reports from the current financial form. "
            "The PDF can be previewed on screen before download."
            if language == "en"
            else "Puedes generar reportes PDF, Word y Excel con los datos financieros actuales del formulario. "
            "El PDF se puede previsualizar en pantalla antes de descargarlo."
        )
    elif any(word in text for word in ["riesgo", "risk", "mora", "pago", "saldo"]):
        topics.append("risk")
        answer = (
            "The risk score combines the trained neural model with the user's credit limit, payment delays, "
            "billed balances and payments. Higher late payments and low payment coverage increase risk."
            if language == "en"
            else "El riesgo combina el modelo neuronal entrenado con limite de credito, mora, saldos facturados "
            "y pagos realizados. Mayor mora y baja cobertura de pago elevan el riesgo."
        )
    else:
        topics.append("help")
        answer = (
            "I can help with the selected neural model, reports, statistical validation, risk interpretation, "
            "and the Render/Vercel deployment."
            if language == "en"
            else "Puedo ayudarte con el modelo neuronal seleccionado, reportes, validacion estadistica, "
            "interpretacion del riesgo y despliegue en Render/Vercel."
        )

    return {"answer": answer, "language": language, "topics": topics}


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "name": "Asesor Financiero Personal IA API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "model_mode": predictor.mode}


@app.get("/model-info")
def model_info() -> Dict:
    return {
        "mode": predictor.mode,
        "features": FEATURE_COLUMNS,
        "metadata": predictor.metadata,
        "sample_payload": DEFAULT_SAMPLE,
    }


@app.get("/statistics/validation")
def statistics_validation() -> Dict:
    return statistical_validation_summary()


@app.post("/chatbot", response_model=ChatbotResponse)
def chatbot(request: ChatbotRequest) -> Dict:
    return chatbot_answer(request.message, request.language)


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> Dict:
    return predictor.predict(request.model_dump())


@app.post("/reports/financial/pdf")
def financial_report_pdf(request: PredictionRequest) -> Response:
    context = report_context(request)
    return report_response(
        build_pdf_report(context),
        "reporte_financiero_programa.pdf",
        "application/pdf",
        inline=True,
    )


@app.post("/reports/financial/docx")
def financial_report_docx(request: PredictionRequest) -> Response:
    context = report_context(request)
    return report_response(
        build_docx_report(context),
        "reporte_financiero_programa.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.post("/reports/financial/xlsx")
def financial_report_xlsx(request: PredictionRequest) -> Response:
    context = report_context(request)
    return report_response(
        build_xlsx_report(context),
        "reporte_financiero_programa.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
