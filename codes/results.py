# results.py
import pandas as pd
import plotly.express as px
import os
from tkinter import messagebox
import numpy as np

def save_efficiency_plot(coeffs, points, title, ylabel, filename_base, results_dir):
    # genera range x per il plot (da minimo a massimo x dei punti)
    x_vals = np.linspace(min(x for x, y in points), max(x for x, y in points), 100)
    y_vals = np.polyval(coeffs, x_vals)

    df = pd.DataFrame({'x': x_vals, 'y': y_vals})

    fig = px.line(df, x='x', y='y', title=title, labels={'x': 'Compression ratio', 'y': ylabel})

    # salva file con nome unico
    path = os.path.join(results_dir, f"{filename_base}.html")
    
    # usa la stessa funzione per nome univoco (da import results)
    path = get_unique_filepath(path)
    fig.write_html(path)
    return path

def get_unique_filepath(filepath):
    if not os.path.exists(filepath):
        return filepath
    base, ext = os.path.splitext(filepath)
    i = 1
    new_filepath = f"{base}({i}){ext}"
    while os.path.exists(new_filepath):
        i += 1
        new_filepath = f"{base}({i}){ext}"
    return new_filepath

def get_results_dir():
    """Restituisce il percorso della cartella 'results' accanto allo script, creandola se necessario."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def save_csv(df, path):
    """Salva il DataFrame in un file CSV nel percorso specificato."""
    df.to_csv(path)

def save_heatmap(df, refrigerant, path):
    """Crea e mostra una heatmap interattiva con Plotly, con hover personalizzato."""
    fig = px.imshow(
        df.values,
        labels=dict(
            x="Evaporation Temp (°C)",
            y="Condensation Temp (°C)",
            color="Heating Power"
        ),
        x=df.columns,
        y=df.index,
        color_continuous_scale='YlOrRd',
        origin='lower'
    )

    fig.update_layout(title=f'Heating Power Map [{refrigerant}]')

    fig.update_traces(
        hovertemplate='Heating Power: %{z:.0f} W<br>Evaporation Temp: %{x}°C<br>Condensation Temp: %{y}°C<extra></extra>'
    )
    
    # Salva l'HTML nella stessa cartella
    fig.write_html(path)

def save_electrical_power_map(df, refrigerant, path):
    fig = px.imshow(
        df.values,
        labels=dict(
            x="Evaporation Temp (°C)",
            y="Condensation Temp (°C)",
            color="Electrical Power"
        ),
        x=df.columns,
        y=df.index,
        color_continuous_scale='YlOrRd',
        origin='lower'
    )

    fig.update_layout(title=f'Electrical Power Map [{refrigerant}]')

    fig.update_traces(
        hovertemplate='Electrical Power: %{z:.0f} W<br>Evaporation Temp: %{x}°C<br>Condensation Temp: %{y}°C<extra></extra>'
    )
    
    # Salva l'HTML nella stessa cartella
    fig.write_html(path)

def save_cop_map(df, refrigerant, path):
    fig = px.imshow(
        df.values,
        labels=dict(
            x="Evaporation Temp (°C)",
            y="Condensation Temp (°C)",
            color="cop"
        ),
        x=df.columns,
        y=df.index,
        color_continuous_scale='YlOrRd',
        origin='lower'
    )

    fig.update_layout(title=f'cop [{refrigerant}]')

    fig.update_traces(
        hovertemplate='COP: %{z:.2f} <br>Evaporation Temp: %{x}°C<br>Condensation Temp: %{y}°C<extra></extra>'
    )
    
    # Salva l'HTML nella stessa cartella
    fig.write_html(path)