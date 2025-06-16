# results.py
import pandas as pd
import plotly.express as px
import os
from tkinter import messagebox

def get_results_dir():
    """Restituisce il percorso della cartella 'results' accanto allo script, creandola se necessario."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def save_csv(df, path):
    """Salva il DataFrame in un file CSV nel percorso specificato."""
    df.to_csv(path)
    messagebox.showinfo("Success", f"Results saved to {path}")

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
        hovertemplate='Heating Power: %{z:.0f} kW<br>Evaporation Temp: %{x}°C<br>Condensation Temp: %{y}°C<extra></extra>'
    )
    
    # Salva l'HTML nella stessa cartella
    fig.write_html(path)