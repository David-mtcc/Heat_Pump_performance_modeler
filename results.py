import pandas as pd
import plotly.express as px
import os
from tkinter import messagebox
import numpy as np

def save_efficiency_plot(coeffs, points, title, ylabel, filename_base, results_dir):
    # Generate x range for the plot (from min to max x of the given points)
    x_vals = np.linspace(min(x for x, y in points), max(x for x, y in points), 100)
    y_vals = np.polyval(coeffs, x_vals)

    df = pd.DataFrame({'x': x_vals, 'y': y_vals})

    fig = px.line(df, x='x', y='y', title=title, labels={'x': 'Compression ratio', 'y': ylabel})

    # Save file with a unique name
    path = os.path.join(results_dir, f"{filename_base}.html")
    
    # Use the same function for unique filename (from import results)
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
    """Returns the path of the 'results' folder next to the script, creating it if needed."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def save_csv(df, path):
    """Saves the DataFrame as a CSV file in the specified path."""
    df.to_csv(path)

def save_heatmap(df, refrigerant, path):
    """Creates and saves an interactive heatmap with Plotly, with customized hover text."""
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
    
    # Save HTML in the same folder
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
    
    # Save HTML in the same folder
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
    
    # Save HTML in the same folder
    fig.write_html(path)
