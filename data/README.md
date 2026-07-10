# Dataset publico

Dataset seleccionado para el articulo:

- Nombre: Default of Credit Card Clients.
- Fuente: UCI Machine Learning Repository.
- Area: negocio / finanzas.
- Tarea: clasificacion binaria.
- Registros: 30.000.
- Variables predictoras: 23.
- Variable objetivo: incumplimiento de pago en el mes siguiente.

El pipeline intenta descargarlo automaticamente con `ucimlrepo`.
Si la descarga no funciona, descarga manualmente el archivo desde UCI y colocalo en:

```text
data/raw/default of credit card clients.xls
```

Despues ejecuta:

```bash
python -m ml.training_pipeline --folds 5 --epochs 20 --batch-size 128
```
