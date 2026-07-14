from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from docx import Document
from docx.shared import Inches
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from pydantic import BaseModel, Field

from ml.predictor import FinancialRiskPredictor
from ml.schema import DEFAULT_SAMPLE, FEATURE_COLUMNS
from ml.statistical_validation import statistical_validation_summary


class PredictionRequest(BaseModel):
    model_name: str = Field("LSTM", pattern="^(MLP|LSTM|GRU|CNN_LSTM|CNN-LSTM|LSTM_ATTENTION|LSTM-ATTENTION)$")
    LIMIT_BAL: float = Field(..., ge=1, le=10_000_000, description="Monto de credito concedido")
    SEX: int = Field(2, ge=1, le=2)
    EDUCATION: int = Field(2, ge=1, le=4)
    MARRIAGE: int = Field(1, ge=1, le=3)
    AGE: int = Field(..., ge=18, le=100)
    PAY_0: int = Field(0, ge=-2, le=9)
    PAY_2: int = Field(0, ge=-2, le=9)
    PAY_3: int = Field(0, ge=-2, le=9)
    PAY_4: int = Field(0, ge=-2, le=9)
    PAY_5: int = Field(0, ge=-2, le=9)
    PAY_6: int = Field(0, ge=-2, le=9)
    BILL_AMT1: float = Field(0, ge=0, le=10_000_000)
    BILL_AMT2: float = Field(0, ge=0, le=10_000_000)
    BILL_AMT3: float = Field(0, ge=0, le=10_000_000)
    BILL_AMT4: float = Field(0, ge=0, le=10_000_000)
    BILL_AMT5: float = Field(0, ge=0, le=10_000_000)
    BILL_AMT6: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT1: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT2: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT3: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT4: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT5: float = Field(0, ge=0, le=10_000_000)
    PAY_AMT6: float = Field(0, ge=0, le=10_000_000)


class PredictionResponse(BaseModel):
    probability: float
    risk_label: str
    mode: str
    threshold: float
    prediction: int
    explanation: List[str]
    model_name: str
    requested_model: str = "LSTM"
    model_available: bool = False
    model_status: str = ""
    artifact_path: Optional[str] = None


class ChatbotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=600)
    language: str = Field("es", pattern="^(es|en)$")
    prediction_context: Optional[Dict[str, Any]] = None


class ChatbotResponse(BaseModel):
    answer: str
    language: str
    topics: List[str]
    sources: List[str] = Field(default_factory=list)
    context_used: bool = False


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

RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMITED_PATHS = {
    "/predict",
    "/chatbot",
    "/reports/financial/pdf",
    "/reports/financial/docx",
    "/reports/financial/xlsx",
}
_request_log: Dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "POST" and request.url.path in RATE_LIMITED_PATHS:
        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        now = time.monotonic()
        bucket = _request_log[key]
        while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Limite de uso alcanzado. Espera un minuto antes de volver a intentar.",
                    "limit": RATE_LIMIT_MAX_REQUESTS,
                    "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
                },
            )
        bucket.append(now)
    return await call_next(request)


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

ACADEMIC_KNOWLEDGE = [
    {
        "id": "dataset_uci_credit_card",
        "keywords": ["dataset", "uci", "datos", "variables", "credit card", "taiwan"],
        "es": (
            "El sistema se basa en el dataset publico UCI Default of Credit Card Clients, "
            "con variables de limite de credito, perfil del cliente, historial de mora, saldos facturados y pagos."
        ),
        "en": (
            "The system is based on the public UCI Default of Credit Card Clients dataset, "
            "with credit limit, client profile, delay history, billed balances and payment variables."
        ),
    },
    {
        "id": "model_catalog",
        "keywords": ["modelo", "model", "lstm", "gru", "mlp", "cnn", "attention", "hibrido", "hybrid"],
        "es": (
            "La investigacion compara tres modelos neuronales clasicos (MLP, LSTM, GRU) y dos hibridos "
            "(CNN-LSTM y LSTM-Attention). El modelo guardado se consume desde FastAPI para evitar reentrenar."
        ),
        "en": (
            "The research compares three classic neural models (MLP, LSTM, GRU) and two hybrid models "
            "(CNN-LSTM and LSTM-Attention). The saved model is consumed from FastAPI to avoid retraining."
        ),
    },
    {
        "id": "statistical_validation",
        "keywords": ["estadistica", "statistical", "wilcoxon", "t-test", "cross", "fold", "validacion"],
        "es": (
            "La validacion incluye cross validation configurable de 5 folds, comparacion de metricas y pruebas "
            "estadisticas pareadas como t-test y Wilcoxon para contrastar diferencias entre modelos."
        ),
        "en": (
            "Validation includes configurable 5-fold cross validation, metric comparison and paired statistical "
            "tests such as t-test and Wilcoxon to contrast model differences."
        ),
    },
    {
        "id": "reports_module",
        "keywords": ["reporte", "report", "pdf", "word", "excel", "descargar", "download"],
        "es": (
            "El modulo de reportes genera PDF, Word y Excel del analisis financiero del programa, incluyendo "
            "resultado, indicadores, recomendaciones y datos ingresados."
        ),
        "en": (
            "The reports module generates PDF, Word and Excel files for the program's financial analysis, "
            "including result, indicators, recommendations and entered data."
        ),
    },
    {
        "id": "operational_xai",
        "keywords": ["explica", "explain", "xai", "shap", "porque", "why", "riesgo", "risk"],
        "es": (
            "La explicabilidad operativa resume factores como mora reciente, cobertura de pagos, uso del credito, "
            "limite aprobado y edad. Es una aproximacion interpretable para acompanar la prediccion neuronal."
        ),
        "en": (
            "Operational explainability summarizes factors such as recent delay, payment coverage, credit usage, "
            "approved limit and age. It is an interpretable approximation that accompanies the neural prediction."
        ),
    },
]


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


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def operational_risk_drivers(payload: Dict) -> List[Dict[str, Any]]:
    indicators = financial_indicators(payload)
    limit_bal = float(payload.get("LIMIT_BAL", 0))
    age = int(float(payload.get("AGE", 0)))
    drivers: List[Dict[str, Any]] = []

    if indicators["max_delay"] > 0:
        drivers.append(
            {
                "factor": "Mora reciente",
                "direction": "increase",
                "impact": round(clamp(0.05 + indicators["max_delay"] * 0.055, 0.05, 0.32), 3),
                "detail": f"{int(indicators['max_delay'])} meses de atraso maximo detectado.",
            }
        )
    if indicators["payment_coverage"] < 0.08:
        drivers.append(
            {
                "factor": "Cobertura de pagos",
                "direction": "increase",
                "impact": round(clamp(0.14 - indicators["payment_coverage"], 0.06, 0.18), 3),
                "detail": f"Cobertura acumulada de {percent(indicators['payment_coverage'])}.",
            }
        )
    elif indicators["payment_coverage"] > 0.18:
        drivers.append(
            {
                "factor": "Cobertura de pagos",
                "direction": "reduce",
                "impact": round(clamp(indicators["payment_coverage"] * 0.34, 0.06, 0.18), 3),
                "detail": f"Cobertura acumulada de {percent(indicators['payment_coverage'])}.",
            }
        )
    if indicators["credit_usage"] > 0.65:
        drivers.append(
            {
                "factor": "Uso de credito",
                "direction": "increase",
                "impact": round(clamp((indicators["credit_usage"] - 0.55) * 0.22, 0.05, 0.20), 3),
                "detail": f"Uso promedio de {percent(indicators['credit_usage'])}.",
            }
        )
    elif indicators["credit_usage"] < 0.25:
        drivers.append(
            {
                "factor": "Uso de credito",
                "direction": "reduce",
                "impact": round(clamp((0.3 - indicators["credit_usage"]) * 0.28, 0.04, 0.12), 3),
                "detail": f"Uso promedio de {percent(indicators['credit_usage'])}.",
            }
        )
    if limit_bal >= 250000:
        drivers.append(
            {
                "factor": "Capacidad aprobada",
                "direction": "reduce",
                "impact": 0.07,
                "detail": f"Limite de credito de {money(limit_bal)}.",
            }
        )
    elif 0 < limit_bal < 80000:
        drivers.append(
            {
                "factor": "Capacidad aprobada",
                "direction": "increase",
                "impact": 0.06,
                "detail": f"Limite de credito de {money(limit_bal)}.",
            }
        )
    if 0 < age < 25:
        drivers.append(
            {"factor": "Madurez financiera", "direction": "increase", "impact": 0.04, "detail": f"Edad: {age} anos."}
        )
    elif age >= 45:
        drivers.append(
            {"factor": "Madurez financiera", "direction": "reduce", "impact": 0.04, "detail": f"Edad: {age} anos."}
        )

    return sorted(drivers, key=lambda item: item["impact"], reverse=True)[:5]


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
    result = predictor.predict(payload, request.model_name)
    indicators = financial_indicators(payload)
    return {
        "payload": payload,
        "result": result,
        "indicators": indicators,
        "drivers": operational_risk_drivers(payload),
        "recommendations": recommendations(result, indicators),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def build_pdf_report(context: Dict) -> bytes:
    payload = context["payload"]
    result = context["result"]
    indicators = context["indicators"]
    drivers = context["drivers"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(10, 13, 20)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_xy(12, 10)
    pdf.cell(0, 9, "Asesor Financiero IA", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(16, 24, 40)
    pdf.ln(12)
    pdf.set_font("helvetica", "B", 15)
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
    pdf.cell(0, 8, "Factores explicativos", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 10)
    if drivers:
        for driver in drivers:
            sign = "+" if driver["direction"] == "increase" else "-"
            pdf.multi_cell(
                0,
                6,
                f"- {driver['factor']}: {sign}{percent(driver['impact'])}. {driver['detail']}",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
    else:
        pdf.multi_cell(0, 6, "El perfil no muestra factores extremos de riesgo.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
    drivers = context["drivers"]

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

    doc.add_heading("Factores explicativos", level=2)
    if drivers:
        for driver in drivers:
            sign = "+" if driver["direction"] == "increase" else "-"
            doc.add_paragraph(
                f"{driver['factor']}: {sign}{percent(driver['impact'])}. {driver['detail']}",
                style="List Bullet",
            )
    else:
        doc.add_paragraph("El perfil no muestra factores extremos de riesgo.")

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
    drivers = context["drivers"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"

    title_fill = PatternFill("solid", fgColor="0A0D14")
    header_fill = PatternFill("solid", fgColor="E8EEF5")
    good_fill = PatternFill("solid", fgColor="DDF7E8")
    warning_fill = PatternFill("solid", fgColor="FFF2CC")
    danger_fill = PatternFill("solid", fgColor="FAD6DB")
    thin_border = Border(bottom=Side(style="thin", color="D9E2EA"))
    bold = Font(bold=True)
    white_bold = Font(bold=True, color="FFFFFF")

    def style_row(sheet, row_number: int, fill: PatternFill = header_fill) -> None:
        for cell in sheet[row_number]:
            cell.font = bold
            cell.fill = fill
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

    ws.append(["Reporte financiero del programa", context["generated_at"]])
    style_row(ws, 1, title_fill)
    ws["A1"].font = white_bold
    ws["B1"].font = white_bold
    ws.append(["Modelo", result["model_name"], "Modo", result["mode"]])
    ws.append([])
    ws.append(["Resultado", "Valor"])
    style_row(ws, 4)
    for row in [
        ("Probabilidad de incumplimiento", percent(result["probability"])),
        ("Nivel de riesgo", result["risk_label"].upper()),
        ("Umbral", percent(result["threshold"])),
        ("Decision", "incumplimiento probable" if result["prediction"] else "sin incumplimiento probable"),
    ]:
        ws.append(row)
    risk_row = 6
    ws[f"B{risk_row}"].fill = (
        danger_fill if result["risk_label"] == "alto" else warning_fill if result["risk_label"] == "medio" else good_fill
    )

    ws.append([])
    ws.append(["Indicador", "Valor"])
    style_row(ws, 10)
    for row in [
        ("Saldos totales", money(indicators["total_bills"])),
        ("Pagos totales", money(indicators["total_payments"])),
        ("Uso promedio de credito", percent(indicators["credit_usage"])),
        ("Cobertura pago / saldo", percent(indicators["payment_coverage"])),
        ("Mora maxima", f"{int(indicators['max_delay'])} meses" if indicators["max_delay"] > 0 else "Sin mora"),
    ]:
        ws.append(row)

    ws.append([])
    ws.append(["Factores explicativos", "Impacto"])
    style_row(ws, ws.max_row)
    if drivers:
        for driver in drivers:
            sign = "+" if driver["direction"] == "increase" else "-"
            ws.append([f"{driver['factor']} - {driver['detail']}", f"{sign}{percent(driver['impact'])}"])
            ws.cell(ws.max_row, 2).fill = danger_fill if driver["direction"] == "increase" else good_fill
    else:
        ws.append(["Sin factores extremos detectados", "0%"])

    ws.append([])
    ws.append(["Recomendaciones"])
    style_row(ws, ws.max_row)
    for item in context["recommendations"]:
        ws.append([item])

    data_ws = wb.create_sheet("Datos ingresados")
    data_ws.append(["Variable", "Valor mostrado", "Valor numerico"])
    style_row(data_ws, 1)
    for key in FEATURE_COLUMNS:
        data_ws.append([FIELD_LABELS.get(key, key), display_value(key, payload[key]), payload[key]])
        current_row = data_ws.max_row
        if key.startswith("PAY_AMT"):
            data_ws.cell(current_row, 2).fill = good_fill if float(payload[key]) > 0 else warning_fill
        elif key.startswith("PAY_"):
            data_ws.cell(current_row, 2).fill = danger_fill if float(payload[key]) > 0 else good_fill

    chart_ws = wb.create_sheet("Saldos vs Pagos")
    chart_ws.append(["Mes", "Saldo", "Pago"])
    style_row(chart_ws, 1)
    for month in range(1, 7):
        chart_ws.append([f"M{month}", float(payload[f"BILL_AMT{month}"]), float(payload[f"PAY_AMT{month}"])])
    chart = BarChart()
    chart.title = "Saldos facturados vs pagos"
    chart.y_axis.title = "Soles"
    chart.x_axis.title = "Mes"
    chart.add_data(Reference(chart_ws, min_col=2, max_col=3, min_row=1, max_row=7), titles_from_data=True)
    chart.set_categories(Reference(chart_ws, min_col=1, min_row=2, max_row=7))
    chart_ws.add_chart(chart, "E2")

    for sheet in [ws, data_ws, chart_ws]:
        sheet.freeze_panes = "A2"
        sheet.column_dimensions["A"].width = 38
        sheet.column_dimensions["B"].width = 30
        sheet.column_dimensions["C"].width = 18
        sheet.column_dimensions["D"].width = 18
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

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


def retrieve_knowledge(message: str, language: str, limit: int = 3) -> List[Dict[str, str]]:
    text = message.lower()
    scored = []
    for item in ACADEMIC_KNOWLEDGE:
        score = sum(1 for keyword in item["keywords"] if keyword in text)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [
        {"id": item["id"], "text": item[language]}
        for _, item in scored[:limit]
    ]


def summarize_prediction_context(prediction_context: Optional[Dict[str, Any]], language: str) -> str:
    if not prediction_context:
        return ""
    probability = prediction_context.get("probability")
    risk_label = prediction_context.get("risk_label")
    model_name = prediction_context.get("model_name")
    drivers = prediction_context.get("drivers") or []
    if probability is None:
        return ""

    try:
        probability_text = percent(float(probability))
    except (TypeError, ValueError):
        probability_text = str(probability)

    driver_text = ""
    if drivers:
        driver_parts = []
        for driver in drivers[:3]:
            label = driver.get("factor") or driver.get("label") or "factor"
            direction = driver.get("direction", "increase")
            direction_text = "aumenta" if direction == "increase" else "reduce"
            if language == "en":
                direction_text = "increases" if direction == "increase" else "reduces"
            impact = driver.get("impact")
            impact_text = f" {percent(float(impact))}" if isinstance(impact, (int, float)) else ""
            driver_parts.append(f"{label} ({direction_text}{impact_text})")
        driver_text = "; ".join(driver_parts)

    if language == "en":
        base = f"Current evaluation: {probability_text} risk, label {risk_label}, model {model_name}."
        return f"{base} Main factors: {driver_text}." if driver_text else base
    base = f"Evaluacion actual: {probability_text} de riesgo, nivel {risk_label}, modelo {model_name}."
    return f"{base} Factores principales: {driver_text}." if driver_text else base


def chatbot_answer(message: str, language: str, prediction_context: Optional[Dict[str, Any]] = None) -> Dict:
    text = message.lower()
    stats = statistical_validation_summary()
    topics: List[str] = []
    retrieved = retrieve_knowledge(message, language)
    context_summary = summarize_prediction_context(prediction_context, language)
    context_used = bool(context_summary)

    asks_current_risk = any(word in text for word in ["porque", "por que", "why", "18", "riesgo", "risk", "resultado"])

    if context_summary and asks_current_risk:
        topics.append("dynamic_context")
        if language == "en":
            answer = (
                f"{context_summary} This means the assistant is reading the last simulated profile, not only a generic rule. "
                "Operational XAI uses the payment delays, payment coverage, credit usage and approved limit to explain the neural result."
            )
        else:
            answer = (
                f"{context_summary} Esto significa que el asistente esta leyendo la ultima simulacion, no solo una regla generica. "
                "La XAI operativa usa mora, cobertura de pagos, uso del credito y limite aprobado para explicar la salida neuronal."
            )
    elif any(word in text for word in ["modelo", "model", "lstm", "red", "neural"]):
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

    if retrieved:
        sources_text = " ".join(item["text"] for item in retrieved)
        if language == "en":
            answer = f"{answer}\n\nProject context: {sources_text}"
        else:
            answer = f"{answer}\n\nContexto del proyecto: {sources_text}"

    return {
        "answer": answer,
        "language": language,
        "topics": topics,
        "sources": [item["id"] for item in retrieved],
        "context_used": context_used,
    }


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
        "available_models": predictor.available_models(),
        "sample_payload": DEFAULT_SAMPLE,
    }


@app.get("/statistics/validation")
def statistics_validation() -> Dict:
    summary = statistical_validation_summary()
    summary["available_models"] = predictor.available_models()
    return summary


@app.post("/chatbot", response_model=ChatbotResponse)
def chatbot(request: ChatbotRequest) -> Dict:
    return chatbot_answer(request.message, request.language, request.prediction_context)


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> Dict:
    return predictor.predict(request.model_dump(), request.model_name)


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
