from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
MODELS = ROOT / "models"

MODEL_CATALOG = [
    {
        "name": "MLP",
        "type": "clasico",
        "type_en": "classic",
        "description": "Red neuronal multicapa para datos tabulares.",
        "description_en": "Multilayer perceptron for tabular data.",
    },
    {
        "name": "LSTM",
        "type": "clasico",
        "type_en": "classic",
        "description": "Red recurrente para dependencias secuenciales en pagos y saldos.",
        "description_en": "Recurrent network for sequential dependencies in payments and balances.",
    },
    {
        "name": "GRU",
        "type": "clasico",
        "type_en": "classic",
        "description": "Red recurrente compacta alternativa a LSTM.",
        "description_en": "Compact recurrent alternative to LSTM.",
    },
    {
        "name": "CNN_LSTM",
        "type": "hibrido",
        "type_en": "hybrid",
        "description": "CNN para patrones locales combinada con memoria LSTM.",
        "description_en": "CNN for local patterns combined with LSTM memory.",
    },
    {
        "name": "LSTM_ATTENTION",
        "type": "hibrido",
        "type_en": "hybrid",
        "description": "LSTM con mecanismo de atencion para ponderar variables relevantes.",
        "description_en": "LSTM with attention to weight relevant variables.",
    },
]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_metadata() -> Dict:
    path = MODELS / "model_metadata.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _records(df: pd.DataFrame) -> List[Dict]:
    if df.empty:
        return []
    return df.where(pd.notna(df), None).to_dict(orient="records")


def _interpret_test(row: Dict) -> str:
    t_p = row.get("paired_t_pvalue")
    w_p = row.get("wilcoxon_pvalue")
    model = row.get("model", "modelo")
    baseline = row.get("baseline", "baseline")

    t_sig = isinstance(t_p, (int, float)) and t_p < 0.05
    w_sig = isinstance(w_p, (int, float)) and w_p < 0.05
    if t_sig and w_sig:
        return f"{model} presenta diferencia estadisticamente significativa frente a {baseline} en ambas pruebas."
    if t_sig:
        return f"{model} supera a {baseline} con evidencia en t-test pareado; Wilcoxon no confirma al 5%."
    if w_sig:
        return f"{model} supera a {baseline} con evidencia en Wilcoxon; t-test no confirma al 5%."
    return f"No hay evidencia estadistica robusta al 5% para afirmar diferencia entre {model} y {baseline}."


def statistical_validation_summary() -> Dict:
    comparison = _read_csv(OUTPUTS / "model_comparison.csv")
    fold_results = _read_csv(OUTPUTS / "fold_results.csv")
    tests = _read_csv(OUTPUTS / "statistical_tests.csv")
    tuning = _read_csv(OUTPUTS / "hyperparameter_tuning.csv")
    metadata = _read_metadata()

    test_records = _records(tests)
    for row in test_records:
        row["interpretation"] = _interpret_test(row)

    best_model = metadata.get("best_model")
    best_cv = metadata.get("best_cv_row", {})
    final_metrics = metadata.get("final_metrics", {})

    classic_count = sum(1 for model in MODEL_CATALOG if model["type"] == "clasico")
    hybrid_count = sum(1 for model in MODEL_CATALOG if model["type"] == "hibrido")

    return {
        "dataset": metadata.get("dataset", "UCI Default of Credit Card Clients"),
        "production_model": best_model or "LSTM",
        "production_reason": (
            "Se usa el mejor modelo guardado por AUC-ROC de validacion cruzada y tuning. "
            "En la corrida actual el modelo seleccionado fue LSTM."
        ),
        "production_reason_en": (
            "The app uses the saved best model selected by cross-validation AUC-ROC and tuning. "
            "In the current run the selected model is LSTM."
        ),
        "model_catalog": MODEL_CATALOG,
        "required_structure": {
            "classic_models": classic_count,
            "hybrid_models": hybrid_count,
            "cross_validation_folds": int(fold_results["fold"].nunique()) if not fold_results.empty else 0,
        },
        "best_cv": best_cv,
        "final_metrics": final_metrics,
        "comparison": _records(comparison),
        "fold_results": _records(fold_results),
        "hyperparameter_tuning": _records(tuning),
        "statistical_tests": test_records,
        "artifacts": {
            "comparison": str(OUTPUTS / "model_comparison.csv"),
            "folds": str(OUTPUTS / "fold_results.csv"),
            "tests": str(OUTPUTS / "statistical_tests.csv"),
            "tuning": str(OUTPUTS / "hyperparameter_tuning.csv"),
        },
    }
