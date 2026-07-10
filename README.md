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
- API temporal Vercel: https://deploybackend-mu.vercel.app

Para cumplir estrictamente la indicacion del docente, el backend debe publicarse en Render conectando este repositorio y usando `render.yaml`.

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

No se inventan métricas. Las tablas del artículo quedan preparadas para completarse con los resultados reales generados por `ml.training_pipeline`.
