from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

from ml.schema import FEATURE_COLUMNS, UCI_RENAME_MAP


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
MODELS = ROOT / "models"


@dataclass
class TrainConfig:
    folds: int = 5
    epochs: int = 20
    batch_size: int = 128
    random_state: int = 42
    run_tuning: bool = True
    save_all_models: bool = True


def import_tensorflow():
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers

        tf.random.set_seed(42)
        return tf, keras, layers
    except Exception as exc:
        raise RuntimeError(
            "TensorFlow no esta instalado. Ejecuta pip install -r requirements.txt "
            "antes de entrenar modelos neuronales."
        ) from exc


def load_uci_dataset() -> pd.DataFrame:
    """Load UCI Default of Credit Card Clients from ucimlrepo or a local file."""
    try:
        from ucimlrepo import fetch_ucirepo

        dataset = fetch_ucirepo(id=350)
        features = dataset.data.features.copy()
        target = dataset.data.targets.copy()
        df = pd.concat([features, target], axis=1)
    except Exception:
        candidates = list(DATA_RAW.glob("*.xls")) + list(DATA_RAW.glob("*.xlsx")) + list(DATA_RAW.glob("*.csv"))
        if not candidates:
            raise FileNotFoundError(
                "No se pudo descargar el dataset UCI ni encontrar archivo local en data/raw/. "
                "Descarga el archivo 'default of credit card clients.xls' desde UCI y colocalo en data/raw/."
            )
        path = candidates[0]
        if path.suffix.lower() in {".xls", ".xlsx"}:
            df = pd.read_excel(path, header=1)
        else:
            df = pd.read_csv(path)

    df = df.rename(columns=UCI_RENAME_MAP)
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])

    target_candidates = [
        "DEFAULT_NEXT_MONTH",
        "default payment next month",
        "Y",
    ]
    target = next((column for column in target_candidates if column in df.columns), None)
    if target is None:
        raise ValueError("No se encontro la variable objetivo de incumplimiento.")

    df = df.rename(columns={target: "DEFAULT_NEXT_MONTH"})
    required = FEATURE_COLUMNS + ["DEFAULT_NEXT_MONTH"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {missing}")

    df = df[required].copy()
    for column in required:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna()
    df["DEFAULT_NEXT_MONTH"] = df["DEFAULT_NEXT_MONTH"].astype(int)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED / "uci_default_credit_clean.csv", index=False)
    return df


def run_eda(df: pd.DataFrame) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    summary = df.describe().T
    summary["missing"] = df.isna().sum()
    summary.to_csv(OUTPUTS / "eda_summary.csv")

    class_distribution = df["DEFAULT_NEXT_MONTH"].value_counts(normalize=False).rename("count")
    class_distribution.to_csv(OUTPUTS / "class_distribution.csv")

    plt.figure(figsize=(12, 9))
    corr = df.corr(numeric_only=True)
    sns.heatmap(corr, cmap="coolwarm", center=0, linewidths=0.1)
    plt.title("Mapa de calor de correlaciones")
    plt.tight_layout()
    plt.savefig(OUTPUTS / "correlation_heatmap.png", dpi=180)
    plt.close()

    plt.figure(figsize=(5, 4))
    sns.countplot(data=df, x="DEFAULT_NEXT_MONTH")
    plt.title("Distribucion de clases")
    plt.xlabel("Incumplimiento proximo mes")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(OUTPUTS / "class_distribution.png", dpi=180)
    plt.close()


def make_mlp(input_dim: int, learning_rate: float = 0.001):
    _, keras, layers = import_tensorflow()
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim,)),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.25),
            layers.Dense(32, activation="relu"),
            layers.Dropout(0.15),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def make_lstm(input_dim: int, learning_rate: float = 0.001):
    _, keras, layers = import_tensorflow()
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim, 1)),
            layers.LSTM(48),
            layers.Dropout(0.25),
            layers.Dense(24, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def make_gru(input_dim: int, learning_rate: float = 0.001):
    _, keras, layers = import_tensorflow()
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim, 1)),
            layers.GRU(48),
            layers.Dropout(0.25),
            layers.Dense(24, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def make_cnn_lstm(input_dim: int, learning_rate: float = 0.001):
    _, keras, layers = import_tensorflow()
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim, 1)),
            layers.Conv1D(filters=32, kernel_size=3, activation="relu", padding="same"),
            layers.MaxPooling1D(pool_size=2),
            layers.LSTM(32),
            layers.Dropout(0.2),
            layers.Dense(16, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def make_lstm_attention(input_dim: int, learning_rate: float = 0.001):
    _, keras, layers = import_tensorflow()
    inputs = keras.Input(shape=(input_dim, 1))
    x = layers.LSTM(48, return_sequences=True)(inputs)
    attention = layers.MultiHeadAttention(num_heads=2, key_dim=8)(x, x)
    x = layers.Add()([x, attention])
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.25)(x)
    x = layers.Dense(24, activation="relu")(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


MODEL_BUILDERS: Dict[str, Tuple[str, Callable[[int, float], object]]] = {
    "MLP": ("tabular", make_mlp),
    "LSTM": ("sequence", make_lstm),
    "GRU": ("sequence", make_gru),
    "CNN_LSTM": ("sequence", make_cnn_lstm),
    "LSTM_ATTENTION": ("sequence", make_lstm_attention),
}


def reshape_for_model(values: np.ndarray, input_shape: str) -> np.ndarray:
    if input_shape == "sequence":
        return values.reshape((values.shape[0], values.shape[1], 1))
    return values


def evaluate_predictions(y_true: np.ndarray, probabilities: np.ndarray) -> Dict[str, float]:
    labels = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": accuracy_score(y_true, labels),
        "precision": precision_score(y_true, labels, zero_division=0),
        "recall": recall_score(y_true, labels, zero_division=0),
        "f1": f1_score(y_true, labels, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probabilities),
    }


def cross_validate_models(X: pd.DataFrame, y: pd.Series, config: TrainConfig) -> pd.DataFrame:
    tf, _, _ = import_tensorflow()
    records: List[Dict] = []
    fold_scores: Dict[str, List[float]] = {name: [] for name in MODEL_BUILDERS}

    splitter = StratifiedKFold(n_splits=config.folds, shuffle=True, random_state=config.random_state)

    for fold, (train_index, valid_index) in enumerate(splitter.split(X, y), start=1):
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X.iloc[train_index])
        X_valid = scaler.transform(X.iloc[valid_index])
        y_train = y.iloc[train_index].to_numpy()
        y_valid = y.iloc[valid_index].to_numpy()

        for model_name, (input_shape, builder) in MODEL_BUILDERS.items():
            tf.keras.backend.clear_session()
            start = time.perf_counter()
            model = builder(X_train.shape[1], 0.001)
            model.fit(
                reshape_for_model(X_train, input_shape),
                y_train,
                validation_data=(reshape_for_model(X_valid, input_shape), y_valid),
                epochs=config.epochs,
                batch_size=config.batch_size,
                verbose=0,
            )
            elapsed = time.perf_counter() - start
            probabilities = model.predict(reshape_for_model(X_valid, input_shape), verbose=0).ravel()
            metrics = evaluate_predictions(y_valid, probabilities)
            fold_scores[model_name].append(metrics["roc_auc"])
            records.append(
                {
                    "model": model_name,
                    "fold": fold,
                    "input_shape": input_shape,
                    "fit_seconds": elapsed,
                    **metrics,
                }
            )

    fold_path = OUTPUTS / "fold_results.csv"
    pd.DataFrame(records).to_csv(fold_path, index=False)

    comparison = (
        pd.DataFrame(records)
        .groupby(["model", "input_shape"], as_index=False)
        .agg(
            accuracy_mean=("accuracy", "mean"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
            f1_mean=("f1", "mean"),
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            fit_seconds_mean=("fit_seconds", "mean"),
        )
        .sort_values("roc_auc_mean", ascending=False)
    )
    comparison.to_csv(OUTPUTS / "model_comparison.csv", index=False)

    baseline = comparison.iloc[-1]["model"]
    stats_records = []
    for model_name, scores in fold_scores.items():
        if model_name == baseline:
            continue
        t_stat, t_p = stats.ttest_rel(scores, fold_scores[baseline])
        try:
            w_stat, w_p = stats.wilcoxon(scores, fold_scores[baseline])
        except ValueError:
            w_stat, w_p = np.nan, np.nan
        stats_records.append(
            {
                "model": model_name,
                "baseline": baseline,
                "paired_t_stat": t_stat,
                "paired_t_pvalue": t_p,
                "wilcoxon_stat": w_stat,
                "wilcoxon_pvalue": w_p,
            }
        )
    pd.DataFrame(stats_records).to_csv(OUTPUTS / "statistical_tests.csv", index=False)
    return comparison


def tune_best_model(
    model_name: str,
    input_shape: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_valid: np.ndarray,
    y_valid: np.ndarray,
    config: TrainConfig,
) -> Tuple[object, Dict]:
    tf, _, _ = import_tensorflow()
    builder = MODEL_BUILDERS[model_name][1]
    grid = [
        {"learning_rate": 0.001, "batch_size": config.batch_size},
        {"learning_rate": 0.0005, "batch_size": config.batch_size},
        {"learning_rate": 0.001, "batch_size": max(32, config.batch_size // 2)},
    ]
    best = None
    best_record = {"roc_auc": -1.0}
    tuning_records = []

    for params in grid:
        tf.keras.backend.clear_session()
        start = time.perf_counter()
        model = builder(X_train.shape[1], params["learning_rate"])
        model.fit(
            reshape_for_model(X_train, input_shape),
            y_train,
            validation_data=(reshape_for_model(X_valid, input_shape), y_valid),
            epochs=config.epochs,
            batch_size=params["batch_size"],
            verbose=0,
        )
        elapsed = time.perf_counter() - start
        probabilities = model.predict(reshape_for_model(X_valid, input_shape), verbose=0).ravel()
        metrics = evaluate_predictions(y_valid, probabilities)
        record = {"model": model_name, "fit_seconds": elapsed, **params, **metrics}
        tuning_records.append(record)
        if metrics["roc_auc"] > best_record["roc_auc"]:
            best = model
            best_record = record

    pd.DataFrame(tuning_records).to_csv(OUTPUTS / "hyperparameter_tuning.csv", index=False)
    return best, best_record


def plot_final_artifacts(model, input_shape: str, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    probabilities = model.predict(reshape_for_model(X_test, input_shape), verbose=0).ravel()
    metrics = evaluate_predictions(y_test, probabilities)
    labels = (probabilities >= 0.5).astype(int)
    matrix = confusion_matrix(y_test, labels)

    plt.figure(figsize=(5, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues")
    plt.title("Matriz de confusion")
    plt.xlabel("Prediccion")
    plt.ylabel("Real")
    plt.tight_layout()
    plt.savefig(OUTPUTS / "confusion_matrix.png", dpi=180)
    plt.close()

    fpr, tpr, _ = roc_curve(y_test, probabilities)
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, label=f"AUC = {metrics['roc_auc']:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.title("Curva ROC")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(OUTPUTS / "roc_curve.png", dpi=180)
    plt.close()
    return metrics


def train_final_model(df: pd.DataFrame, comparison: pd.DataFrame, config: TrainConfig) -> Dict:
    X = df[FEATURE_COLUMNS]
    y = df["DEFAULT_NEXT_MONTH"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=config.random_state
    )
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_train, y_train, test_size=0.20, stratify=y_train, random_state=config.random_state
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_valid_scaled = scaler.transform(X_valid)
    X_test_scaled = scaler.transform(X_test)

    best_row = comparison.iloc[0]
    best_name = best_row["model"]
    input_shape = best_row["input_shape"]

    if config.run_tuning:
        model, tuning_record = tune_best_model(
            best_name,
            input_shape,
            X_train_scaled,
            y_train.to_numpy(),
            X_valid_scaled,
            y_valid.to_numpy(),
            config,
        )
    else:
        builder = MODEL_BUILDERS[best_name][1]
        model = builder(X_train_scaled.shape[1], 0.001)
        model.fit(
            reshape_for_model(X_train_scaled, input_shape),
            y_train.to_numpy(),
            validation_data=(reshape_for_model(X_valid_scaled, input_shape), y_valid.to_numpy()),
            epochs=config.epochs,
            batch_size=config.batch_size,
            verbose=0,
        )
        tuning_record = {}

    final_metrics = plot_final_artifacts(model, input_shape, X_test_scaled, y_test.to_numpy())

    MODELS.mkdir(parents=True, exist_ok=True)
    model.save(MODELS / "best_model.keras")
    model.save(MODELS / "best_model.h5")
    model.save(MODELS / f"{best_name}.keras")
    joblib.dump(scaler, MODELS / "preprocessor.joblib")
    model_artifacts = {
        best_name: {
            "path": str((MODELS / f"{best_name}.keras").relative_to(ROOT)),
            "input_shape": input_shape,
            "source": "best_tuned_model",
        }
    }

    if config.save_all_models:
        tf, _, _ = import_tensorflow()
        for candidate_name, (candidate_shape, builder) in MODEL_BUILDERS.items():
            if candidate_name == best_name:
                continue
            tf.keras.backend.clear_session()
            start = time.perf_counter()
            candidate_model = builder(X_train_scaled.shape[1], 0.001)
            candidate_model.fit(
                reshape_for_model(X_train_scaled, candidate_shape),
                y_train.to_numpy(),
                validation_data=(reshape_for_model(X_valid_scaled, candidate_shape), y_valid.to_numpy()),
                epochs=config.epochs,
                batch_size=config.batch_size,
                verbose=0,
            )
            elapsed = time.perf_counter() - start
            candidate_path = MODELS / f"{candidate_name}.keras"
            candidate_model.save(candidate_path)
            model_artifacts[candidate_name] = {
                "path": str(candidate_path.relative_to(ROOT)),
                "input_shape": candidate_shape,
                "source": "final_architecture_fit",
                "fit_seconds": elapsed,
            }

    metadata = {
        "best_model": best_name,
        "input_shape": input_shape,
        "feature_columns": FEATURE_COLUMNS,
        "final_metrics": final_metrics,
        "best_cv_row": best_row.to_dict(),
        "best_tuning_record": tuning_record,
        "model_artifacts": model_artifacts,
        "dataset": "UCI Default of Credit Card Clients",
    }
    (MODELS / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--no-tuning", action="store_true")
    parser.add_argument("--no-save-all-models", action="store_true")
    args = parser.parse_args()

    config = TrainConfig(
        folds=args.folds,
        epochs=args.epochs,
        batch_size=args.batch_size,
        run_tuning=not args.no_tuning,
        save_all_models=not args.no_save_all_models,
    )
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    df = load_uci_dataset()
    run_eda(df)
    comparison = cross_validate_models(df[FEATURE_COLUMNS], df["DEFAULT_NEXT_MONTH"], config)
    metadata = train_final_model(df, comparison, config)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
