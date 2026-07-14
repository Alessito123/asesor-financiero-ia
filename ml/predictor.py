from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import joblib
import numpy as np
import pandas as pd

from ml.schema import FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[1]

MODEL_INPUT_SHAPES = {
    "MLP": "tabular",
    "LSTM": "sequence",
    "GRU": "sequence",
    "CNN_LSTM": "sequence",
    "LSTM_ATTENTION": "sequence",
}


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
        self.model_cache: Dict[str, object] = {}
        self.preprocessor = None
        self.metadata: Dict = {}
        self.comparison_rows: List[Dict] = []
        self.mode = "baseline"
        self._load()

    def _load(self) -> None:
        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        self.comparison_rows = self._load_comparison_rows()

        if not self.model_path.exists() or not self.preprocessor_path.exists():
            return

        try:
            cache_dir = Path(tempfile.gettempdir()) / "asesor_financiero_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))

            import tensorflow as tf

            self.model = tf.keras.models.load_model(self.model_path)
            self.model_cache[self.production_model_name] = self.model
            self.preprocessor = joblib.load(self.preprocessor_path)
            self.mode = "trained"
        except Exception as exc:  # pragma: no cover - environment-dependent
            self.metadata["load_warning"] = str(exc)
            self.model = None
            self.preprocessor = None
            self.mode = "baseline"

    @property
    def production_model_name(self) -> str:
        return self._normalize_model_name(self.metadata.get("best_model", "LSTM")) or "LSTM"

    @staticmethod
    def _normalize_model_name(model_name: Optional[str]) -> Optional[str]:
        if not model_name:
            return None
        normalized = str(model_name).strip().upper().replace("-", "_").replace(" ", "_")
        aliases = {
            "LSTM_ATT": "LSTM_ATTENTION",
            "ATTENTION": "LSTM_ATTENTION",
            "CNNLSTM": "CNN_LSTM",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in MODEL_INPUT_SHAPES else None

    def _load_comparison_rows(self) -> List[Dict]:
        path = ROOT / "outputs" / "model_comparison.csv"
        if not path.exists():
            return []
        try:
            frame = pd.read_csv(path)
            return frame.where(pd.notna(frame), None).to_dict(orient="records")
        except Exception:
            return []

    def _artifact_path(self, model_name: str) -> Optional[Path]:
        artifacts = self.metadata.get("model_artifacts", {})
        if model_name in artifacts:
            path = Path(artifacts[model_name].get("path", ""))
            if not path.is_absolute():
                path = ROOT / path
            if path.exists():
                return path
        candidates = [
            self.model_path if model_name == self.production_model_name else None,
            self.model_path.parent / f"{model_name}.keras",
            self.model_path.parent / f"{model_name}.h5",
            self.model_path.parent / f"model_{model_name}.keras",
            self.model_path.parent / f"model_{model_name}.h5",
        ]
        return next((path for path in candidates if path and path.exists()), None)

    def _input_shape_for_model(self, model_name: str) -> str:
        artifacts = self.metadata.get("model_artifacts", {})
        if model_name in artifacts and artifacts[model_name].get("input_shape"):
            return artifacts[model_name]["input_shape"]
        if model_name == self.production_model_name and self.metadata.get("input_shape"):
            return self.metadata["input_shape"]
        return MODEL_INPUT_SHAPES.get(model_name, "sequence")

    def _load_model_for_name(self, model_name: str):
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        artifact_path = self._artifact_path(model_name)
        if not artifact_path or not self.preprocessor_path.exists():
            return None
        try:
            import tensorflow as tf

            model = tf.keras.models.load_model(artifact_path)
            self.model_cache[model_name] = model
            if self.preprocessor is None:
                self.preprocessor = joblib.load(self.preprocessor_path)
            return model
        except Exception as exc:  # pragma: no cover - environment-dependent
            self.metadata.setdefault("model_load_warnings", {})[model_name] = str(exc)
            return None

    def available_models(self) -> List[Dict]:
        rows_by_model = {row.get("model"): row for row in self.comparison_rows}
        models = []
        for model_name, input_shape in MODEL_INPUT_SHAPES.items():
            artifact_path = self._artifact_path(model_name)
            comparison = rows_by_model.get(model_name, {})
            models.append(
                {
                    "name": model_name,
                    "input_shape": comparison.get("input_shape") or self._input_shape_for_model(model_name) or input_shape,
                    "artifact_exists": bool(artifact_path),
                    "artifact_path": str(artifact_path) if artifact_path else None,
                    "is_production": model_name == self.production_model_name,
                    "status": "trained" if artifact_path else "proxy",
                    "roc_auc_mean": comparison.get("roc_auc_mean"),
                    "f1_mean": comparison.get("f1_mean"),
                }
            )
        return models

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
    def _proxy_probability(payload: Dict, model_name: str) -> float:
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
        weights = {
            "MLP": (-1.65, 0.85, 1.25, -1.05),
            "GRU": (-1.90, 0.70, 1.10, -0.85),
            "CNN_LSTM": (-2.15, 0.65, 1.00, -0.75),
            "LSTM_ATTENTION": (-1.80, 1.05, 1.35, -1.25),
            "LSTM": (-1.75, 0.95, 1.40, -1.20),
        }
        intercept, delay_w, usage_w, payment_w = weights.get(model_name, weights["LSTM"])
        z = intercept + delay_w * avg_delay + usage_w * utilization + payment_w * payment_ratio + age_factor
        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def _risk_label(probability: float) -> str:
        if probability >= 0.70:
            return "alto"
        if probability >= 0.40:
            return "medio"
        return "bajo"

    @staticmethod
    def _explain(payload: Dict, probability: float, mode: str, model_name: str, artifact_exists: bool) -> Iterable[str]:
        notes = []
        if mode == "baseline":
            notes.append("Prediccion generada con linea base explicable; ejecutar entrenamiento para usar el modelo final.")
        elif not artifact_exists:
            notes.append(
                f"Modelo {model_name} seleccionado como simulacion academica; aun no existe artefacto entrenado guardado."
            )
        else:
            notes.append(f"Prediccion generada con el modelo entrenado {model_name} guardado en models/.")

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

    def predict(self, payload: Dict, model_name: Optional[str] = None) -> Dict:
        payload = {column: float(payload.get(column, 0)) for column in FEATURE_COLUMNS}
        requested_model = self._normalize_model_name(model_name) or self.production_model_name
        selected_model = requested_model
        artifact_path = self._artifact_path(selected_model)
        model = self._load_model_for_name(selected_model)
        artifact_exists = model is not None and self.preprocessor is not None

        if artifact_exists:
            frame = self._payload_to_frame(payload)
            transformed = self.preprocessor.transform(frame)
            if self._input_shape_for_model(selected_model) == "sequence":
                transformed = transformed.reshape((transformed.shape[0], transformed.shape[1], 1))
            probability = float(model.predict(transformed, verbose=0).ravel()[0])
            mode = "trained" if selected_model == self.production_model_name else "trained_selected"
        elif selected_model in MODEL_INPUT_SHAPES:
            probability = self._proxy_probability(payload, selected_model)
            mode = "proxy"
        else:
            probability = self._baseline_probability(payload)
            selected_model = "baseline_explica"
            artifact_path = None
            artifact_exists = False
            mode = "baseline"

        probability = max(0.0, min(1.0, probability))
        label = self._risk_label(probability)
        return {
            "probability": round(probability, 4),
            "risk_label": label,
            "mode": mode,
            "threshold": 0.5,
            "prediction": int(probability >= 0.5),
            "explanation": list(self._explain(payload, probability, mode, selected_model, artifact_exists)),
            "model_name": selected_model,
            "requested_model": requested_model,
            "model_available": artifact_exists,
            "model_status": "trained artifact" if artifact_exists else "academic proxy",
            "artifact_path": str(artifact_path) if artifact_path else None,
        }
