import os
import pandas as pd
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

    return render(request, 'charge_csv.html', {
        'Columns': column,
        'Data': data,
        'graphic_data': graphic_data,
    })

