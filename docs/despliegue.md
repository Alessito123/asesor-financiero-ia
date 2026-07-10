# Guia de despliegue

## Backend FastAPI en Render

1. Subir el proyecto a GitHub.
2. Entrar a Render y crear un nuevo Web Service.
3. Conectar el repositorio.
4. Usar estos comandos para una API liviana con modo fallback:

```text
Build Command: pip install -r requirements-app.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Si vas a subir `models/best_model.keras` y consumir el modelo neuronal real, usa `pip install -r requirements.txt` para incluir TensorFlow.

Backend temporal desplegado en Vercel para demo publica:

```text
https://deploybackend-mu.vercel.app
```

Cuando tengas el repositorio en GitHub, Render puede crear el servicio desde `render.yaml`.

5. Configurar variables de entorno si aplica:

```text
MODEL_PATH=models/best_model.keras
PREPROCESSOR_PATH=models/preprocessor.joblib
MODEL_METADATA_PATH=models/model_metadata.json
```

6. Probar:

```text
https://tu-api.onrender.com/health
https://tu-api.onrender.com/docs
```

## Frontend Streamlit

Streamlit no es el despliegue natural de Vercel porque necesita un proceso Python persistente. Opciones recomendadas:

- Streamlit Community Cloud.
- Render Web Service con `streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`.

## Frontend auxiliar en Vercel

La carpeta `vercel_frontend/` incluye una pantalla HTML/JS que consume el backend FastAPI.

Despliegue realizado:

```text
https://vercelfrontend-peach.vercel.app
```

El frontend actualmente consume:

```text
https://deploybackend-mu.vercel.app
```

En Vercel:

1. Importar el repositorio.
2. Configurar el proyecto como sitio estatico.
3. Definir la URL del backend en el archivo `vercel_frontend/app.js` o exponerla como variable durante el build.

## GitHub

Comandos base:

```bash
git init
git add .
git commit -m "Proyecto asesor financiero IA"
git branch -M main
git remote add origin https://github.com/usuario/repositorio.git
git push -u origin main
```

## Jira

Crear un proyecto Scrum o Kanban y registrar las historias de `docs/jira_backlog.md`.
