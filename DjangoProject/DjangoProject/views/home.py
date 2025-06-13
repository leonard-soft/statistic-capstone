import os

import numpy as np
import pandas as pd
from django.shortcuts import render
from django.conf import settings
import json
from scipy import stats


def home(request):
    rute_csv = os.path.join(settings.BASE_DIR, 'csv', 'ai_dev_productivity.csv')

    df = None
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

    estadisticas = []
    cuartil_productivity = {}
    frecuencias = {}
    probabilidad_info = []
    predicciones = []
    modelo_regresion = {}

    graph_data = {}  # <-- Definir acá para que siempre exista

    if df is not None:
        cuantitativas = [
            "hours_coding",
            "coffee_intake_mg",
            "sleep_hours",
            "commits",
            "bugs_reported",
            "ai_usage_hours",
            "cognitive_load"
        ]

        for col in cuantitativas:
            if col in df.columns:
                valores = df[col].dropna()
                media = valores.mean()
                mediana = valores.median()
                moda = valores.mode()
                if not moda.empty:
                    moda_val = moda.iloc[0]
                else:
                    moda_val = "Sin moda"
                desv = valores.std()
                estadisticas.append([col, round(media, 2), round(mediana, 2), moda_val, round(desv, 2)])

        # Cálculos adicionales para probabilidad y predicciones
        if 'commits' in df.columns and 'hours_coding' in df.columns:
            df = df[df['hours_coding'] != 0].copy()
            df['productividad'] = df['commits'] / df['hours_coding']
            productividad = df['productividad'].dropna()

            cuartil_productivity = {
                'min': round(productividad.min(), 2),
                'q1': round(productividad.quantile(0.25), 2),
                'q2': round(productividad.median(), 2),
                'q3': round(productividad.quantile(0.75), 2),
                'max': round(productividad.max(), 2),
                'p10': round(productividad.quantile(0.10), 2),
                'p25': round(productividad.quantile(0.25), 2),
                'p50': round(productividad.quantile(0.50), 2),
                'p75': round(productividad.quantile(0.75), 2),
                'p90': round(productividad.quantile(0.90), 2),
                'media': round(productividad.mean(), 2),
                'std_dev': round(productividad.std(), 2),
            }

            # Ejemplo de probabilidad
            umbral_p80 = productividad.quantile(0.8)
            p_prod_mayor_80 = (productividad > umbral_p80).mean()
            print(productividad)
            print(round(p_prod_mayor_80, 2))
            probabilidad_info.append(["P (Productividad > 80)", round(p_prod_mayor_80, 2)])

        df['productividad'] = df['commits'] / df['hours_coding']

        df['productividad'] = df['productividad'].replace([np.inf, -np.inf], np.nan).dropna()

        grupos = df.groupby(['ai_usage_hours', 'bugs_reported'])

        resultados = []

        for (ai, bugs), grupo in grupos:
            prod = grupo['productividad'].dropna()
            n = len(prod)
            if n < 2:
                continue

            media = prod.mean()
            std = prod.std(ddof=1)
            sem = std / np.sqrt(n)

            # 95% de confianza
            t_crit = stats.t.ppf(1 - 0.025, df=n - 1)
            margen_error = t_crit * sem
            ic = [media - margen_error, media + margen_error]

            predicciones.append({
                'uso_IA': ai,
                'bugs': bugs,
                'promedio_productividad': round(media, 2),
                'intervalo_confianza_95': [round(ic[0], 2), round(ic[1], 2)],
                'n': n
            })

        variables_frecuencia = ['distractions', 'task_success', 'bugs_reported', 'commits']
        for var in variables_frecuencia:
            if var in df.columns:
                frecuencia_absoluta = df[var].value_counts().sort_index()
                frecuencia_relativa = df[var].value_counts(normalize=True).sort_index()
                frecuencia_acumulada = frecuencia_absoluta.cumsum()
                frecuencia_relativa_acumulada = frecuencia_relativa.cumsum()

                frecuencia_df = pd.DataFrame({
                    'valor': frecuencia_absoluta.index,
                    'frecuencia_absoluta': frecuencia_absoluta.values,
                    'frecuencia_relativa': frecuencia_relativa.values,
                    'frecuencia_acumulada': frecuencia_acumulada.values,
                    'frecuencia_relativa_acumulada': frecuencia_relativa_acumulada.values
                })

                frecuencias[var] = frecuencia_df.to_dict('records')

        # Gráficos
        if 'hours_coding' in df.columns:
            bins = 10
            hist = pd.cut(df['hours_coding'], bins=bins)
            hist_counts = df.groupby(hist, observed=True).size().tolist()
            bin_edges = pd.cut(df['hours_coding'], bins=bins).cat.categories
            bin_labels = [str(interval) for interval in bin_edges]
            graph_data['histogram'] = {
                'labels': bin_labels,
                'counts': hist_counts
            }

        if 'task_success' in df.columns:
            pie_counts = df['task_success'].value_counts().sort_index()
            pie_labels = pie_counts.index.astype(int).map({0: 'fail', 1: 'success'}).tolist()
            pie_values = pie_counts.values.tolist()

            graph_data['pie'] = {
                'labels': pie_labels,
                'values': pie_values
            }

        if 'bugs_reported' in df.columns and 'distractions' in df.columns:
            grouped = df.groupby('distractions')['bugs_reported'].mean().sort_index()
            graph_data['bar_bugs_distractions'] = {
                'labels': grouped.index.astype(str).tolist(),
                'values': grouped.round(2).tolist()
            }

        if 'commits' in df.columns and 'hours_coding' in df.columns:
            bins = [0, 1, 2, 4, 6, 8, 10, 24]
            labels = ["0-1", "1-2", "2-4", "4-6", "6-8", "8-10", "10+"]
            df['hours_bin'] = pd.cut(df['hours_coding'], bins=bins, labels=labels, right=False)
            grouped_commits = df.groupby('hours_bin', observed=True)['commits'].mean().round(2)
            graph_data['bar_productivity'] = {
                'labels': grouped_commits.index.astype(str).tolist(),
                'values': grouped_commits.fillna(0).tolist()
            }

        if 'coffee_intake_mg' in df.columns and 'cognitive_load' in df.columns:
            scatter_points = df[['coffee_intake_mg', 'cognitive_load']].dropna()
            graph_data['scatter'] = {
                'x': scatter_points['coffee_intake_mg'].tolist(),
                'y': scatter_points['cognitive_load'].tolist()
            }



    return render(request, 'charge_csv.html', {
        'Columns': column,
        'Data': data,
        'graphic_data': graphic_data,
        'estadisticas': estadisticas,
        'cuartil_productivity': cuartil_productivity,
        'frecuencias': frecuencias,
        'graph_data_json': json.dumps(graph_data),
        'probabilidad_info': probabilidad_info,
        'predicciones': predicciones,
        'modelo_regresion': modelo_regresion
    })
