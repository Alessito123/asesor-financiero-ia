from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from ml.predictor import FinancialRiskPredictor
from ml.schema import DEFAULT_SAMPLE, FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "docs" / "articulo_cientifico_asesor_financiero_ia.docx"
METRICS_PATH = ROOT / "outputs" / "model_comparison.csv"


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f8fb;
            color: #17202f;
        }
        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stSidebar"] {
            background: #0f766e;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dce3e8;
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(22, 32, 47, 0.08);
            padding: 16px;
        }
        div[data-testid="stForm"] {
            background: #ffffff;
            border: 1px solid #dce3e8;
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(22, 32, 47, 0.08);
            padding: 18px;
        }
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border: 0;
            border-radius: 8px;
            background: #0f766e;
            color: #ffffff;
            font-weight: 800;
        }
        .premium-banner {
            border: 1px solid #dce3e8;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 12px 30px rgba(22, 32, 47, 0.08);
            padding: 18px 20px;
            margin: 0 0 18px;
        }
        .premium-banner strong {
            display: block;
            color: #0f766e;
            font-size: 0.85rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        .premium-banner span {
            display: block;
            color: #647083;
            margin-top: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def backend_url() -> str:
    return st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


def check_login() -> bool:
    if st.session_state.get("logged_in"):
        return True

    st.set_page_config(page_title="Asesor Financiero IA", page_icon="IA", layout="wide")
    apply_theme()
    st.title("Asesor Financiero Personal IA")
    st.caption("Ingreso al dashboard academico")

    with st.form("login"):
        user = st.text_input("Usuario", value="")
        password = st.text_input("Contrasena", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)

    expected_user = st.secrets.get("APP_USER", os.getenv("APP_USER", "admin"))
    expected_password = st.secrets.get("APP_PASSWORD", os.getenv("APP_PASSWORD", "admin123"))

    if submitted:
        if user == expected_user and password == expected_password:
            st.session_state["logged_in"] = True
            st.rerun()
        st.error("Credenciales invalidas")

    st.info("Demo local: usuario admin, contrasena admin123. Cambiar en .env o Streamlit secrets.")
    return False


def call_prediction(payload: Dict) -> Dict:
    url = backend_url().rstrip("/") + "/predict"
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception:
        predictor = FinancialRiskPredictor()
        return predictor.predict(payload)


def prediction_form() -> None:
    st.subheader("Prediccion de riesgo financiero")

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        payload = DEFAULT_SAMPLE.copy()

        with col1:
            payload["LIMIT_BAL"] = st.number_input("Credito concedido (S/)", min_value=1, value=200000, step=10000)
            payload["AGE"] = st.number_input("Edad", min_value=18, max_value=100, value=34)
            payload["SEX"] = st.selectbox("Sexo", options=[1, 2], format_func=lambda x: "Masculino" if x == 1 else "Femenino")
            payload["EDUCATION"] = st.selectbox("Educacion", options=[1, 2, 3, 4], format_func=lambda x: {1: "Posgrado", 2: "Universidad", 3: "Secundaria", 4: "Otros"}[x])
            payload["MARRIAGE"] = st.selectbox("Estado civil", options=[1, 2, 3], format_func=lambda x: {1: "Casado", 2: "Soltero", 3: "Otros"}[x])

        with col2:
            for key in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]:
                payload[key] = st.number_input(key, min_value=-2, max_value=9, value=int(payload[key]))

        with col3:
            for key in ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3"]:
                payload[key] = st.number_input(f"{key} (S/)", min_value=0, value=int(payload[key]), step=1000)

        with st.expander("Meses adicionales"):
            cols = st.columns(3)
            for i, key in enumerate(["BILL_AMT4", "BILL_AMT5", "BILL_AMT6", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]):
                with cols[i % 3]:
                    payload[key] = st.number_input(f"{key} (S/)", min_value=0, value=int(payload[key]), step=1000)

        submitted = st.form_submit_button("Calcular riesgo", use_container_width=True)

    if submitted:
        result = call_prediction(payload)
        probability = result["probability"]
        label = result["risk_label"].upper()
        st.metric("Probabilidad de incumplimiento", f"{probability:.1%}", label)
        st.progress(min(probability, 1.0))
        st.write("Modelo:", result["model_name"], "| modo:", result["mode"])
        for note in result["explanation"]:
            st.info(note)
        st.code(json.dumps({"payload": payload, "resultado": result}, indent=2, ensure_ascii=False), language="json")


def metrics_tab() -> None:
    st.subheader("Comparacion de modelos")
    if METRICS_PATH.exists():
        df = pd.read_csv(METRICS_PATH)
        st.dataframe(df, use_container_width=True)
        metric_col = "roc_auc_mean" if "roc_auc_mean" in df.columns else df.select_dtypes("number").columns[-1]
        fig = px.bar(df, x="model", y=metric_col, color="model", title="Resultado comparativo")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aun no hay metricas reales. Ejecuta: python -m ml.training_pipeline --folds 5")


def dashboard() -> None:
    st.set_page_config(page_title="Asesor Financiero IA", page_icon="IA", layout="wide")
    apply_theme()
    with st.sidebar:
        st.title("Asesor IA")
        st.write("Backend:", backend_url())
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("Dashboard Financiero con IA")
    st.markdown(
        """
        <div class="premium-banner">
            <strong>Analitica crediticia</strong>
            <span>FastAPI, Streamlit y modelos de redes neuronales para evaluar riesgo financiero personal.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Dataset publico", "UCI", "30.000 registros")
    col2.metric("Modelos requeridos", "5", "3 clasicos + 2 hibridos")
    col3.metric("Validacion", "5 folds", "configurable")

    tab1, tab2, tab3, tab4 = st.tabs(["Prediccion", "Modelos", "Articulo", "Despliegue"])

    with tab1:
        prediction_form()

    with tab2:
        metrics_tab()

    with tab3:
        st.subheader("Articulo cientifico")
        if ARTICLE_PATH.exists():
            st.success("El avance del articulo ya fue generado.")
            st.download_button(
                "Descargar Word",
                ARTICLE_PATH.read_bytes(),
                file_name=ARTICLE_PATH.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.warning("Ejecuta: python reports/build_article_docx.py")

    with tab4:
        st.subheader("Checklist de entrega")
        st.checkbox("Backend FastAPI preparado para Render", value=True)
        st.checkbox("Dashboard Streamlit con login", value=True)
        st.checkbox("Frontend auxiliar para Vercel", value=True)
        st.checkbox("Codigo listo para GitHub", value=True)
        st.checkbox("Backlog sugerido para Jira", value=(ROOT / "docs" / "jira_backlog.md").exists())


if __name__ == "__main__":
    if check_login():
        dashboard()
