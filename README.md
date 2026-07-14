# Sistema Asesor Financiero Personal IA

Proyecto académico mejorado para un sistema de asesoría financiera personal con:

- **Frontend principal:** Streamlit.
- **Backend:** FastAPI.
- **Modelo IA:** redes neuronales para predicción de riesgo financiero.
- **Dataset público:** UCI Default of Credit Card Clients.
- **Reportes:** PDF, Word y Excel.
- **Despliegue sugerido:** Render para FastAPI y Vercel para frontend estático auxiliar. Streamlit puede desplegarse en Render o Streamlit Community Cloud.

## Estructura

```text
backend/           API FastAPI para consumir el modelo entrenado
frontend/          Dashboard Streamlit con login, predicción y reportes
ml/                Carga de dataset, EDA, entrenamiento, validación y predicción
reports/           Generadores de reportes y artículo científico
docs/              Artículo científico, guía de despliegue y backlog Jira
vercel_frontend/   Frontend web simple compatible con Vercel
legacy/            Código original preservado
n8n/               Flujo n8n original preservado
```

## Instalación local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-app.txt
copy .env.example .env
```

Para entrenar redes neuronales con TensorFlow, instala tambien:

```bash
pip install -r requirements.txt
```

## Entrenar el modelo

El pipeline usa el dataset público UCI Default of Credit Card Clients. Si hay internet, `ucimlrepo` lo descarga automáticamente.

```bash
python -m ml.training_pipeline --folds 5 --epochs 20 --batch-size 128
```

Salidas principales:

- `models/best_model.keras`
- `models/best_model.h5`
- `models/preprocessor.joblib`
- `models/model_metadata.json`
- `outputs/model_comparison.csv`
- `outputs/confusion_matrix.png`
- `outputs/roc_curve.png`
- `outputs/correlation_heatmap.png`
- `outputs/hyperparameter_tuning.csv`
- `outputs/statistical_tests.csv`

## Ejecutar backend

```bash
uvicorn backend.main:app --reload
```

API local: `http://localhost:8000`

## Ejecutar Streamlit

```bash
streamlit run frontend/streamlit_app.py
```

Credenciales demo por defecto:

- Usuario: `admin`
- Contraseña: `admin123`

## Frontend Vercel

La carpeta `vercel_frontend/` contiene una pantalla web ligera que consume el endpoint `/predict` del backend. En Vercel configura la variable:

```text
BACKEND_URL=https://tu-backend-render.onrender.com
```

Despliegue actual:

- Frontend Vercel: https://vercelfrontend-peach.vercel.app
- Backend Render: https://asesor-financiero-api-wnyk.onrender.com

El backend ya se publico en Render conectando este repositorio y usando `render.yaml`.
La app publica tambien incluye una seccion de reportes del programa: genera con FastAPI un PDF previsualizable y descargas Word/Excel usando los datos financieros actuales del formulario. Los documentos academicos quedan como enlaces secundarios.

## Cumplimiento solicitado por el docente

El programa usa redes neuronales para clasificar riesgo de incumplimiento financiero. El modelo que consume la app en produccion es **LSTM**, guardado en `models/best_model.keras` y `models/best_model.h5`, para no reentrenar en cada prediccion.

Modelos entrenados y comparados:

- 3 modelos clasicos: `MLP`, `LSTM`, `GRU`.
- 2 modelos hibridos: `CNN_LSTM`, `LSTM_ATTENTION`.

La app publica incluye:

- Dashboard con validacion despues de credenciales en Streamlit y simulador web en Vercel.
- Tema claro/oscuro.
- Idioma espanol/ingles.
- Chatbot academico conectado al backend.
- Modulo de pruebas estadisticas en FastAPI: `/statistics/validation`.
- Reportes del programa en PDF, Word y Excel desde los datos actuales del formulario.

## Artículo científico

El avance del artículo está en:

```text
docs/articulo_cientifico_asesor_financiero_ia.docx
```

También se puede regenerar con:

```bash
python reports/build_article_docx.py
```

## Nota académica

No se inventan métricas. Las tablas del artículo y los reportes se alimentan de los archivos reales generados por `ml.training_pipeline`. Para una corrida academica definitiva se recomienda ejecutar con `--epochs 20`; la corrida actual deja artefactos funcionales para validar el flujo completo.

## Entrega final

La evidencia consolidada de despliegue, enlaces publicos, Jira y GitHub esta documentada en:

```text
docs/entrega_final.md
docs/entrega_final_asesor_financiero_ia.docx
```

Resumen de enlaces:

- GitHub: https://github.com/Alessito123/asesor-financiero-ia
- Frontend Vercel: https://vercelfrontend-peach.vercel.app
- Backend Render: https://asesor-financiero-api-wnyk.onrender.com
- Jira: https://asesor-financiero-ia.atlassian.net/jira/software/projects/KAN/list
