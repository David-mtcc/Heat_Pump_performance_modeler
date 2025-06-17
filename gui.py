#guy.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import calc  # modulo di calcolo
import numpy as np
import results  # modulo per la gestione dei risultati
from calc import generate_grid_inside_polygon  # aggiungi questo import

def run_calculation():
    try:
        refrigerant = refrigerant_var.get()
        superheat = float(superheat_entry.get())
        subcool = float(subcool_entry.get())
        displacement_cc = float(displacement_entry.get())
        speed_rps = float(speed_entry.get())

        # Recupera gli 8 punti (T_evap, T_cond)
        points = []
        for i in range(8):
            t_evap_str = evap_entries[i].get()
            t_cond_str = cond_entries[i].get()
            t_evap = float(t_evap_str)
            t_cond = float(t_cond_str)
            points.append((t_evap, t_cond))

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    grid_points = generate_grid_inside_polygon(points, resolution=1.0)
    
    # Chiamata funzioni di calcolo passando i punti
    df_heating_map = calc.build_heating_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        grid_points
    )

    df_electrical_power_map = calc.build_electric_power_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        grid_points
    )

    # Salvataggio risultati heating power
    results_dir = results.get_results_dir()

    csv_path = os.path.join(results_dir, 'heating_power_map.csv')
    results.save_csv(df_heating_map, csv_path)

    html_path = os.path.join(results_dir, 'heating_power_map.html')
    results.save_heatmap(df_heating_map, refrigerant, html_path)

    # Salvataggio risultati electrical power
    csv_path = os.path.join(results_dir, 'electrical_power_map.csv')
    results.save_csv(df_electrical_power_map, csv_path)

    html_path = os.path.join(results_dir, 'electrical_power_map.html')
    results.save_electrical_power_map(df_electrical_power_map, refrigerant, html_path)

    # Salvataggio risultati COP
    cop_map = df_heating_map / df_electrical_power_map
    cop_csv  = os.path.join(results_dir, 'cop_map.csv')
    results.save_csv(cop_map, cop_csv)

    cop_html = os.path.join(results_dir, 'cop_map.html')
    results.save_cop_map(cop_map, refrigerant, cop_html)

    messagebox.showinfo("Success", f"Results saved to {results_dir}")

# Creazione GUI
root = tk.Tk()
root.title("Heat Pump Heating Power Calculator")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

refrigerant_var = tk.StringVar(value='R134a')

ttk.Label(mainframe, text="Select refrigerant:").grid(row=0, column=0, sticky=tk.W)
refrigerant_combo = ttk.Combobox(mainframe, textvariable=refrigerant_var, state="readonly")
refrigerant_combo['values'] = ('R134a', 'R32', 'R290', 'R410A', 'R454B', 'R407C', 'R744')
refrigerant_combo.grid(row=0, column=1)

# Parametri base
labels_basic = [
    "Superheat (K):",
    "Subcooling (K):",
    "Compressor displacement (cc/rev):",
    "Compressor speed (rev/s):"
]

default_values_basic = ['5', '3', '25', '100']
entries_vars = []

for i, (label, default) in enumerate(zip(labels_basic, default_values_basic), start=1):
    ttk.Label(mainframe, text=label).grid(row=i, column=0, sticky=tk.W)
    entry = ttk.Entry(mainframe)
    entry.grid(row=i, column=1)
    entry.insert(0, default)
    entries_vars.append(entry)

superheat_entry, subcool_entry, displacement_entry, speed_entry = entries_vars

# Ora 8 coppie di punti T_evap, T_cond
ttk.Label(mainframe, text="Define 8 points of (Evap Temp °C, Cond Temp °C) envelope:").grid(row=5, column=0, columnspan=2, pady=(10,0))

evap_entries = []
cond_entries = []

default_points = [
    (-20, 35),
    (-15, 30),
    (15, 30),
    (20, 35),
    (20, 55),
    (15, 60),
    (-15, 60),
    (-20, 50)
]

for i, (t_evap_default, t_cond_default) in enumerate(default_points):
    ttk.Label(mainframe, text=f"Point {i+1} Evap Temp (°C):").grid(row=6 + i, column=0, sticky=tk.E)
    evap_entry = ttk.Entry(mainframe, width=10)
    evap_entry.grid(row=6 + i, column=1, sticky=tk.W)
    evap_entry.insert(0, str(t_evap_default))
    evap_entries.append(evap_entry)

    ttk.Label(mainframe, text=f"Cond Temp (°C):").grid(row=6 + i, column=2, sticky=tk.E)
    cond_entry = ttk.Entry(mainframe, width=10)
    cond_entry.grid(row=6 + i, column=3, sticky=tk.W)
    cond_entry.insert(0, str(t_cond_default))
    cond_entries.append(cond_entry)

calc_button = ttk.Button(mainframe, text="Calculate and Save", command=run_calculation)
calc_button.grid(row=14, column=0, columnspan=4, pady=10)

root.mainloop()
