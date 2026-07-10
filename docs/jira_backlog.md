# Backlog sugerido para Jira

## Epica 1: Preparacion del proyecto

- Historia: Ordenar estructura del repositorio.
- Historia: Configurar entorno Python y dependencias.
- Historia: Preservar version original en carpeta legacy.

## Epica 2: Modelo de inteligencia artificial

- Historia: Descargar dataset publico UCI.
- Historia: Ejecutar EDA con limpieza y estadisticos descriptivos.
- Historia: Entrenar modelos MLP, LSTM y GRU.
- Historia: Entrenar modelos hibridos CNN-LSTM y LSTM-Attention.
- Historia: Ejecutar validacion cruzada con 5 folds configurables.
- Historia: Realizar tuning de hiperparametros.
- Historia: Aplicar pruebas estadisticas sobre resultados por fold.
- Historia: Guardar el mejor modelo en formato `.keras` y `.h5`.

## Epica 3: Backend FastAPI

- Historia: Crear endpoint `/predict`.
- Historia: Crear endpoint `/model-info`.
- Historia: Manejar modo fallback si aun no hay modelo entrenado.
- Historia: Documentar API con Swagger.

## Epica 4: Frontend y dashboard

- Historia: Crear login en Streamlit.
- Historia: Crear formulario de prediccion.
- Historia: Visualizar metricas comparativas.
- Historia: Permitir descarga del articulo Word.
- Historia: Crear frontend auxiliar para Vercel.

## Epica 5: Reportes y articulo

- Historia: Generar reporte PDF.
- Historia: Generar reporte Excel.
- Historia: Generar reporte Word.
- Historia: Redactar avance del articulo cientifico.
- Historia: Incluir metodologia, modelos, validacion, tuning y pruebas estadisticas.

## Epica 6: Despliegue

- Historia: Publicar repositorio en GitHub.
- Historia: Desplegar backend en Render.
- Historia: Desplegar frontend auxiliar en Vercel.
- Historia: Documentar credenciales demo y variables de entorno.
