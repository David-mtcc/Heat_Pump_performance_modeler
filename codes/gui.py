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

        x_vol, y_vol = [], []
        for x_e, y_e in volumetric_points_entries:
            x_vol.append(float(x_e.get()))
            y_vol.append(float(y_e.get()))
        volumetric_coeffs = np.polyfit(x_vol, y_vol, 4)
        
        x_iso, y_iso = [], []
        for x_e, y_e in isentropic_points_entries:
            x_iso.append(float(x_e.get()))
            y_iso.append(float(y_e.get()))
        isentropic_coeffs = np.polyfit(x_iso, y_iso, 4)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    grid_points = generate_grid_inside_polygon(points, resolution=1.0)
    
    # Chiamata funzioni di calcolo passando i punti
    df_heating_map = calc.build_heating_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        grid_points, volumetric_coeffs, isentropic_coeffs
    )

    df_electrical_power_map = calc.build_electric_power_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        grid_points, volumetric_coeffs, isentropic_coeffs
    )

    # Salvataggio risultati heating power
    results_dir = results.get_results_dir()

    csv_path = os.path.join(results_dir, 'heating_power_map.csv')
    csv_path = results.get_unique_filepath(csv_path)
    results.save_csv(df_heating_map, csv_path)

    html_path = os.path.join(results_dir, 'heating_power_map.html')
    html_path = results.get_unique_filepath(html_path)
    results.save_heatmap(df_heating_map, refrigerant, html_path)

   # Salvataggio risultati electrical power
    csv_path = os.path.join(results_dir, 'electrical_power_map.csv')
    csv_path = results.get_unique_filepath(csv_path)
    results.save_csv(df_electrical_power_map, csv_path)

    html_path = os.path.join(results_dir, 'electrical_power_map.html')
    html_path = results.get_unique_filepath(html_path)
    results.save_electrical_power_map(df_electrical_power_map, refrigerant, html_path)

    cop_map = df_heating_map / df_electrical_power_map

    # Salvataggio risultati COP
    cop_csv  = os.path.join(results_dir, 'cop_map.csv')
    cop_csv = results.get_unique_filepath(cop_csv)
    results.save_csv(cop_map, cop_csv)

    cop_html = os.path.join(results_dir, 'cop_map.html')
    cop_html = results.get_unique_filepath(cop_html)
    results.save_cop_map(cop_map, refrigerant, cop_html)

    volumetric_plot_path = results.save_efficiency_plot(
        volumetric_coeffs, 
        [(float(x.get()), float(y.get())) for x,y in volumetric_points_entries],
        title="Volumetric Efficiency Curve",
        ylabel="Volumetric Efficiency",
        filename_base="volumetric_efficiency_curve",
        results_dir=results_dir
    )

    isentropic_plot_path = results.save_efficiency_plot(
        isentropic_coeffs, 
        [(float(x.get()), float(y.get())) for x,y in isentropic_points_entries],
        title="Isentropic Efficiency Curve",
        ylabel="Isentropic Efficiency",
        filename_base="isentropic_efficiency_curve",
        results_dir=results_dir
    )

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

# GUI: inserimento punti per volumetric efficiency
volumetric_points_entries = []
ttk.Label(mainframe, text="Volumetric Efficiency: insert 4 points (x, y)").grid(row=15, column=0, columnspan=4, pady=(10,0))
for i in range(4):
    x_entry = ttk.Entry(mainframe, width=6)
    y_entry = ttk.Entry(mainframe, width=6)
    x_entry.grid(row=16+i, column=1)
    y_entry.grid(row=16+i, column=3)
    x_entry.insert(0, str([0, 4, 7, 10][i]))
    y_entry.insert(0, str([0.4, 0.85, 0.6, 0.25][i]))
    ttk.Label(mainframe, text=f"Point {i+1} x:").grid(row=16+i, column=0)
    ttk.Label(mainframe, text=f"y:").grid(row=16+i, column=2)
    volumetric_points_entries.append((x_entry, y_entry))

# GUI: inserimento punti per isentropic efficiency
isentropic_points_entries = []
ttk.Label(mainframe, text="Isentropic Efficiency: insert 4 points (x, y)").grid(row=20, column=0, columnspan=4, pady=(10,0))
for i in range(4):
    x_entry = ttk.Entry(mainframe, width=6)
    y_entry = ttk.Entry(mainframe, width=6)
    x_entry.grid(row=21+i, column=1)
    y_entry.grid(row=21+i, column=3)
    x_entry.insert(0, str([0, 4, 7, 10][i]))
    y_entry.insert(0, str([0.7, 0.8, 0.6, 0.25][i]))
    ttk.Label(mainframe, text=f"Point {i+1} x:").grid(row=21+i, column=0)
    ttk.Label(mainframe, text=f"y:").grid(row=21+i, column=2)
    isentropic_points_entries.append((x_entry, y_entry))

calc_button = ttk.Button(mainframe, text="Calculate and Save", command=run_calculation)
calc_button.grid(row=25, column=0, columnspan=4, pady=10)

root.mainloop()
