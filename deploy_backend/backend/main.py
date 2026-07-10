from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.predictor import FinancialRiskPredictor
from ml.schema import DEFAULT_SAMPLE, FEATURE_COLUMNS


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


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> Dict:
    return predictor.predict(request.model_dump())
