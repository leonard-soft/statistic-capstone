import os
import pandas as pd
import statistics
from django.shortcuts import render
from django.conf import settings

def home(request):
    rute_csv = os.path.join(settings.BASE_DIR, 'csv', 'ai_dev_productivity.csv')

    try:
        df = pd.read_csv(rute_csv)
        column = df.columns.tolist()
        data = df.values.tolist()

        graphic_data = {}
        if len(df.columns) >= 2:
            graphic_data = {
                'label': df.iloc[:, 0].astype(str).tolist(),
                'date': df.iloc[:, 1].tolist()
            }

    except Exception as e:
        column = []
        data = []
        graphic_data = {}
        print(f"Error al leer el CSV: {e}")

    print(f"Ruta CSV: {rute_csv}")
    print(f"Columnas: {column}, Filas: {len(data)}")

    # Variables cuantitativas
    cuantitativas = [
        "hours_coding",
        "coffee_intake_mg",
        "sleep_hours",
        "commits",
        "bugs_reported",
        "ai_usage_hours",
        "cognitive_load"
    ]

    estadisticas = []
    for col in cuantitativas:
        if col in df.columns:
            valores = df[col].dropna()
            media = valores.mean()
            mediana = valores.median()
            try:
                moda = statistics.mode(valores)
            except:
                moda = "Sin moda"
            desv = valores.std()
            estadisticas.append([col, round(media, 2), round(mediana, 2), moda, round(desv, 2)])

    return render(request, 'charge_csv.html', {
        'Columns': column,
        'Data': data,
        'graphic_data': graphic_data,
        'estadisticas': estadisticas,
    })

