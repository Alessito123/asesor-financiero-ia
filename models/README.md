# Modelos

Esta carpeta se llena al ejecutar:

```bash
python -m ml.training_pipeline --folds 5 --epochs 20 --batch-size 128
```

Archivos esperados:

- `best_model.keras`: modelo final recomendado.
- `best_model.h5`: copia compatible con el formato solicitado por el docente.
- `preprocessor.joblib`: escalador/preprocesador usado antes de predecir.
- `model_metadata.json`: métricas, columnas y modelo ganador.
