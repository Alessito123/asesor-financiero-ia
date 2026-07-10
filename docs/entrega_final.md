# Entrega final - Sistema Asesor Financiero Personal IA

Fecha de cierre: 2026-07-10  
Proyecto Jira: KAN - Asesor Financiero IA

## Enlaces de entrega

- Repositorio GitHub: https://github.com/Alessito123/asesor-financiero-ia
- Frontend Vercel: https://vercelfrontend-peach.vercel.app
- Backend Render: https://asesor-financiero-api-wnyk.onrender.com
- Health backend: https://asesor-financiero-api-wnyk.onrender.com/health
- Swagger FastAPI: https://asesor-financiero-api-wnyk.onrender.com/docs
- Jira: https://asesor-financiero-ia.atlassian.net/jira/software/projects/KAN/list

## Estado de despliegue

| Componente | Plataforma | Estado | Evidencia |
| --- | --- | --- | --- |
| Backend FastAPI | Render | Desplegado | `/health` responde `status: ok` y `model_mode: baseline` |
| Frontend web | Vercel | Desplegado | Sitio publico consume el backend de Render |
| Codigo fuente | GitHub | Publicado | Repositorio en `Alessito123/asesor-financiero-ia` |
| Gestion/documentacion | Jira | Configurado | Proyecto `KAN` creado con backlog academico |
| Integracion GitHub-Jira | GitHub for Atlassian | Conectado | GitHub Cloud muestra `Alessito123`, 1 repo, backfill `FINISHED` |

## Evidencia de integracion Jira-GitHub

La integracion quedo conectada mediante **GitHub for Atlassian**:

- Producto: GitHub Cloud.
- Cuenta conectada: `Alessito123`.
- Acceso a repositorios: `Only select repos`.
- Cantidad de repositorios conectados: `1`.
- Estado de backfill: `FINISHED`.
- Permisos: `FULL ACCESS` sobre el repositorio seleccionado.

Nota: `FULL ACCESS` aplica al repo seleccionado por la integracion, no a todos los repositorios, porque la pantalla indica `Only select repos` y cantidad `1`.

Captura de evidencia:

```text
docs/evidencia_jira_github.png
```

## Credenciales demo

Para el dashboard Streamlit local:

```text
Usuario: admin
Contrasena: admin123
```

## Como probar la aplicacion

1. Abrir el frontend:

```text
https://vercelfrontend-peach.vercel.app
```

2. Verificar el estado de la API en pantalla. Debe indicar que la API esta disponible.
3. Completar el formulario financiero y enviar la prediccion.
4. Verificar directamente el backend:

```text
https://asesor-financiero-api-wnyk.onrender.com/health
```

5. Revisar la documentacion Swagger:

```text
https://asesor-financiero-api-wnyk.onrender.com/docs
```

## Documentacion y articulo

Archivos principales:

- Documento Word de entrega: `docs/entrega_final_asesor_financiero_ia.docx`
- Articulo cientifico: `docs/articulo_cientifico_asesor_financiero_ia.docx`
- Guia de despliegue: `docs/despliegue.md`
- Backlog Jira sugerido: `docs/jira_backlog.md`
- Reportes del modelo: `docs/reporte_modelos.pdf`, `docs/reporte_modelos.docx`, `docs/reporte_modelos.xlsx`

## Cumplimiento de indicaciones

| Indicacion docente | Estado |
| --- | --- |
| Backend en Render | Cumplido |
| Frontend en Vercel | Cumplido con frontend web auxiliar |
| Codigo alojado en GitHub | Cumplido |
| Documentacion en Jira | Cumplido con proyecto `KAN` |
| Python con FastAPI | Cumplido |
| Python con Streamlit | Cumplido en `frontend/streamlit_app.py` |
| Dataset publico | Cumplido: UCI Default of Credit Card Clients |
| Articulo cientifico | Cumplido: archivo Word en `docs/` |
| Reportes PDF, Word y Excel | Cumplido en `docs/` |

## Uso de Jira con commits

Para que Jira relacione automaticamente commits futuros con tickets, usar el codigo del ticket en el mensaje:

```bash
git commit -m "KAN-11 documentar despliegue final"
git commit -m "KAN-13 actualizar articulo cientifico"
```

Esto permite que la actividad del repositorio aparezca asociada al proyecto Jira.
