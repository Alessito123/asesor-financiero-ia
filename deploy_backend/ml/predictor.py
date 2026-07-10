from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Dict, Iterable, Optional

import joblib
import numpy as np
import pandas as pd

from ml.schema import FEATURE_COLUMNS


class FinancialRiskPredictor:
    """Load the trained model when available, otherwise use a transparent baseline.

    The fallback keeps the API and Streamlit app usable before the team runs the
    full neural-network training pipeline. It is intentionally labeled as a
    baseline, not as the final scientific model.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        preprocessor_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
    ) -> None:
        self.model_path = Path(model_path or os.getenv("MODEL_PATH", "models/best_model.keras"))
        self.preprocessor_path = Path(
            preprocessor_path or os.getenv("PREPROCESSOR_PATH", "models/preprocessor.joblib")
        )
        self.metadata_path = Path(
            metadata_path or os.getenv("MODEL_METADATA_PATH", "models/model_metadata.json")
        )
        self.model = None
        self.preprocessor = None
        self.metadata: Dict = {}
        self.mode = "baseline"
        self._load()

    def _load(self) -> None:
        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        if not self.model_path.exists() or not self.preprocessor_path.exists():
            return

        try:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(self.model_path)
            self.preprocessor = joblib.load(self.preprocessor_path)
            self.mode = "trained"
        except Exception as exc:  # pragma: no cover - environment-dependent
            self.metadata["load_warning"] = str(exc)
            self.model = None
            self.preprocessor = None
            self.mode = "baseline"

    @staticmethod
    def _payload_to_frame(payload: Dict) -> pd.DataFrame:
        row = {column: payload.get(column, 0) for column in FEATURE_COLUMNS}
        return pd.DataFrame([row], columns=FEATURE_COLUMNS)

    @staticmethod
    def _baseline_probability(payload: Dict) -> float:
        late_payments = [
            float(payload.get(column, 0))
            for column in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
        ]
        bills = [max(float(payload.get(f"BILL_AMT{i}", 0)), 0.0) for i in range(1, 7)]
        payments = [max(float(payload.get(f"PAY_AMT{i}", 0)), 0.0) for i in range(1, 7)]
        limit_bal = max(float(payload.get("LIMIT_BAL", 1)), 1.0)
        age = float(payload.get("AGE", 35))

        avg_delay = sum(max(v, 0.0) for v in late_payments) / len(late_payments)
        utilization = min(sum(bills) / (limit_bal * 6.0), 2.0)
        payment_ratio = sum(payments) / max(sum(bills), 1.0)
        age_factor = 0.15 if age < 25 else 0.0

        z = -1.75 + 0.95 * avg_delay + 1.4 * utilization - 1.2 * payment_ratio + age_factor
        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def _risk_label(probability: float) -> str:
        if probability >= 0.70:
            return "alto"
        if probability >= 0.40:
            return "medio"
        return "bajo"

    @staticmethod
    def _explain(payload: Dict, probability: float, mode: str) -> Iterable[str]:
        notes = []
        if mode == "baseline":
            notes.append("Prediccion generada con linea base explicable; ejecutar entrenamiento para usar el modelo final.")
        else:
            notes.append("Prediccion generada con el modelo entrenado guardado en models/.")

        if max(float(payload.get(col, 0)) for col in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]) > 0:
            notes.append("Existe historial de pago atrasado en al menos un mes.")
        if float(payload.get("LIMIT_BAL", 1)) > 0:
            bill_sum = sum(max(float(payload.get(f"BILL_AMT{i}", 0)), 0.0) for i in range(1, 7))
            utilization = bill_sum / (float(payload.get("LIMIT_BAL", 1)) * 6.0)
            if utilization > 0.75:
                notes.append("La utilizacion promedio del credito es elevada.")
        if probability < 0.40:
            notes.append("El perfil se ubica en zona de menor riesgo relativo.")
        return notes

    def predict(self, payload: Dict) -> Dict:
        payload = {column: float(payload.get(column, 0)) for column in FEATURE_COLUMNS}

        if self.model is not None and self.preprocessor is not None:
            frame = self._payload_to_frame(payload)
            transformed = self.preprocessor.transform(frame)
            if self.metadata.get("input_shape") == "sequence":
                transformed = transformed.reshape((transformed.shape[0], transformed.shape[1], 1))
            probability = float(self.model.predict(transformed, verbose=0).ravel()[0])
        else:
            probability = self._baseline_probability(payload)

        probability = max(0.0, min(1.0, probability))
        label = self._risk_label(probability)
        return {
            "probability": round(probability, 4),
            "risk_label": label,
            "mode": self.mode,
            "threshold": 0.5,
            "prediction": int(probability >= 0.5),
            "explanation": list(self._explain(payload, probability, self.mode)),
            "model_name": self.metadata.get("best_model", "baseline_explica"),
        }
