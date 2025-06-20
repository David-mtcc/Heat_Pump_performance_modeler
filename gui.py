import tkinter as tk
from tkinter import ttk, messagebox
import os
import calc  # modulo di calcolo
import numpy as np
import results  # modulo per la gestione dei risultati
from calc import generate_grid_inside_polygon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def update_plot():
    try:
        x_vol = [float(x.get()) for x, _ in volumetric_points_entries]
        y_vol = [float(y.get()) for _, y in volumetric_points_entries]
        x_iso = [float(x.get()) for x, _ in isentropic_points_entries]
        y_iso = [float(y.get()) for _, y in isentropic_points_entries]

        coeffs_vol = np.polyfit(x_vol, y_vol, 3)
        coeffs_iso = np.polyfit(x_iso, y_iso, 3)

        x_plot = np.linspace(min(x_vol + x_iso), max(x_vol + x_iso), 100)
        y_vol_plot = np.polyval(coeffs_vol, x_plot)
        y_iso_plot = np.polyval(coeffs_iso, x_plot)

        ax.clear()
        ax.plot(x_plot, y_vol_plot, label='Volumetric Efficiency')
        ax.plot(x_plot, y_iso_plot, label='Isentropic Efficiency')
        ax.set_ylim(0, 1)
        ax.set_xlabel('Compression Ratio')
        ax.set_ylabel('Efficiency')
        ax.legend()
        ax.grid(True)

        canvas.draw()
    except:
        pass


def run_calculation():
    try:
        refrigerant = refrigerant_var.get()
        superheat = float(superheat_entry.get())
        subcool = float(subcool_entry.get())
        displacement_cc = float(displacement_entry.get())
        speed_rps = float(speed_entry.get())

        points = []
        for i in range(4):
            t_evap = float(evap_entries[i].get())
            t_cond = float(cond_entries[i].get())
            points.append((t_evap, t_cond))

        x_vol = [float(x.get()) for x, _ in volumetric_points_entries]
        y_vol = [float(y.get()) for _, y in volumetric_points_entries]
        volumetric_coeffs = np.polyfit(x_vol, y_vol, 3)

        x_iso = [float(x.get()) for x, _ in isentropic_points_entries]
        y_iso = [float(y.get()) for _, y in isentropic_points_entries]
        isentropic_coeffs = np.polyfit(x_iso, y_iso, 3)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    grid_points = generate_grid_inside_polygon(points, resolution=1.0)

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

    results_dir = results.get_results_dir()
    results.save_csv(df_heating_map, os.path.join(results_dir, 'heating_power_map.csv'))
    results.save_heatmap(df_heating_map, refrigerant, os.path.join(results_dir, 'heating_power_map.html'))

    results.save_csv(df_electrical_power_map, os.path.join(results_dir, 'electrical_power_map.csv'))
    results.save_electrical_power_map(df_electrical_power_map, refrigerant, os.path.join(results_dir, 'electrical_power_map.html'))

    cop_map = df_heating_map / df_electrical_power_map
    results.save_csv(cop_map, os.path.join(results_dir, 'cop_map.csv'))
    results.save_cop_map(cop_map, refrigerant, os.path.join(results_dir, 'cop_map.html'))

    messagebox.showinfo("Success", f"Results saved to {results_dir}")


root = tk.Tk()
root.title("Heat Pump Heating Power Calculator")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.N))

plot_frame = ttk.Frame(root, padding="10")
plot_frame.grid(row=0, column=1, sticky=(tk.N, tk.E))

refrigerant_var = tk.StringVar(value='R134a')

ttk.Label(mainframe, text="Select refrigerant:").grid(row=0, column=0, sticky=tk.W)
refrigerant_combo = ttk.Combobox(mainframe, textvariable=refrigerant_var, state="readonly")
refrigerant_combo['values'] = ('R134a', 'R32', 'R290', 'R410A', 'R454B', 'R407C', 'R744')
refrigerant_combo.grid(row=0, column=1)

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

ttk.Label(mainframe, text="Define 4 points of (Evap Temp °C, Cond Temp °C) envelope:").grid(row=5, column=0, columnspan=2, pady=(10,0))

evap_entries, cond_entries = [], []
default_points = [(-10, 30), (10, 30), (10, 60), (-10, 60)]

for i, (t_evap, t_cond) in enumerate(default_points):
    ttk.Label(mainframe, text=f"Point {i+1} Evap Temp (°C):").grid(row=6+i, column=0, sticky=tk.E)
    evap_entry = ttk.Entry(mainframe, width=10)
    evap_entry.grid(row=6+i, column=1)
    evap_entry.insert(0, str(t_evap))
    evap_entries.append(evap_entry)

    ttk.Label(mainframe, text=f"Cond Temp (°C):").grid(row=6+i, column=2, sticky=tk.E)
    cond_entry = ttk.Entry(mainframe, width=10)
    cond_entry.grid(row=6+i, column=3)
    cond_entry.insert(0, str(t_cond))
    cond_entries.append(cond_entry)

volumetric_points_entries = []
ttk.Label(mainframe, text="Volumetric Efficiency: insert 4 points (x, y)").grid(row=10, column=0, columnspan=4, pady=(10,0))
for i in range(4):
    x_entry = ttk.Entry(mainframe, width=6)
    y_entry = ttk.Entry(mainframe, width=6)
    x_entry.grid(row=11+i, column=1)
    y_entry.grid(row=11+i, column=3)
    x_entry.insert(0, str([0, 4, 7, 10][i]))
    y_entry.insert(0, str([0.4, 0.85, 0.6, 0.25][i]))
    x_entry.bind('<KeyRelease>', lambda e: update_plot())
    y_entry.bind('<KeyRelease>', lambda e: update_plot())
    ttk.Label(mainframe, text=f"Point {i+1} x:").grid(row=11+i, column=0)
    ttk.Label(mainframe, text=f"y:").grid(row=11+i, column=2)
    volumetric_points_entries.append((x_entry, y_entry))

isentropic_points_entries = []
ttk.Label(mainframe, text="Isentropic Efficiency: insert 4 points (x, y)").grid(row=15, column=0, columnspan=4, pady=(10,0))
for i in range(4):
    x_entry = ttk.Entry(mainframe, width=6)
    y_entry = ttk.Entry(mainframe, width=6)
    x_entry.grid(row=16+i, column=1)
    y_entry.grid(row=16+i, column=3)
    x_entry.insert(0, str([0, 3, 7, 10][i]))
    y_entry.insert(0, str([0.7, 0.75, 0.5, 0.25][i]))
    x_entry.bind('<KeyRelease>', lambda e: update_plot())
    y_entry.bind('<KeyRelease>', lambda e: update_plot())
    ttk.Label(mainframe, text=f"Point {i+1} x:").grid(row=16+i, column=0)
    ttk.Label(mainframe, text=f"y:").grid(row=16+i, column=2)
    isentropic_points_entries.append((x_entry, y_entry))

calc_button = ttk.Button(mainframe, text="Calculate and Save", command=run_calculation)
calc_button.grid(row=21, column=0, columnspan=4, pady=10)

fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack()

update_plot()
root.mainloop()
