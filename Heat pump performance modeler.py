import tkinter as tk
from tkinter import ttk, messagebox
import os
import numpy as np
import pandas as pd

# Funzioni di calcolo (le tieni come prima)
def calculate_heating_power(refrigerant, T_evap, T_cond, superheat, subcool,
                             displacement_cc, speed_rps, eta_isentropic=0.7):
    T_evap_K = T_evap + 273.15
    T_cond_K = T_cond + 273.15

    h1 = PropsSI('H', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    s1 = PropsSI('S', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    h2s = PropsSI('H', 'S', s1, 'T', T_cond_K, refrigerant)
    h2 = h1 + (h2s - h1) / eta_isentropic
    h3 = PropsSI('H', 'T', T_cond_K - subcool, 'Q', 0, refrigerant)

    displacement_m3 = displacement_cc * 1e-6
    vol_flow = displacement_m3 * speed_rps

    rho = PropsSI('D', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    m_dot = vol_flow * rho

    q_cond = h2 - h3
    Q_dot = q_cond * m_dot
    return Q_dot

def build_heating_map(refrigerant, superheat, subcool, displacement_cc, speed_rps,
                      T_evap_min, T_evap_max, T_cond_min, T_cond_max):
    evaps = np.arange(T_evap_min, T_evap_max + 1)
    conds = np.arange(T_cond_min, T_cond_max + 1)
    df = pd.DataFrame(index=conds, columns=evaps, dtype=float)
    df.index.name = 'T_cond (°C)'
    df.columns.name = 'T_evap (°C)'
    for T_cond in conds:
        for T_evap in evaps:
            df.at[T_cond, T_evap] = calculate_heating_power(
                refrigerant, T_evap, T_cond,
                superheat, subcool,
                displacement_cc, speed_rps
            )
    df.index.name = 'T_cond (°C)'
    df.columns.name = 'T_evap (°C)'
    return df

# Funzione callback per il bottone
def run_calculation():
    try:
        refrigerant = refrigerant_var.get()
        superheat = float(superheat_entry.get())
        subcool = float(subcool_entry.get())
        displacement_cc = float(displacement_entry.get())
        speed_rps = float(speed_entry.get())
        T_evap_min = int(evap_min_entry.get())
        T_evap_max = int(evap_max_entry.get())
        T_cond_min = int(cond_min_entry.get())
        T_cond_max = int(cond_max_entry.get())

        if T_evap_max < T_evap_min or T_cond_max < T_cond_min:
            messagebox.showerror("Input Error", "Max temperatures must be >= min temperatures")
            return

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    df_map = build_heating_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        T_evap_min, T_evap_max,
        T_cond_min, T_cond_max
    )

    # Salvataggio nella cartella results accanto al file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    output_file = os.path.join(results_dir, 'heating_power_map.csv')
    df_map.to_csv(output_file)

    messagebox.showinfo("Success", f"Results saved to {output_file}")

# Creazione GUI
root = tk.Tk()
root.title("Heat Pump Heating Power Calculator")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Variabile refrigerante
refrigerant_var = tk.StringVar(value='R134a')

ttk.Label(mainframe, text="Select refrigerant:").grid(row=0, column=0, sticky=tk.W)
#definisco istanza combobox
refrigerant_combo = ttk.Combobox(mainframe, textvariable=refrigerant_var, state="readonly")
refrigerant_combo['values'] = ('R134a', 'R32', 'R290','R410A','R454B','R407C','R744')
refrigerant_combo.grid(row=0, column=1)

# Crea label + entry per tutti gli altri input

labels = [
    "Superheat (K):",
    "Subcooling (K):",
    "Compressor displacement (cc/rev):",
    "Compressor speed (rev/s):",
    "Min evaporation temp (°C):",
    "Max evaporation temp (°C):",
    "Min condensation temp (°C):",
    "Max condensation temp (°C):"
]

entries_vars = []

for i, label in enumerate(labels, start=1):
    ttk.Label(mainframe, text=label).grid(row=i, column=0, sticky=tk.W)
    entry = ttk.Entry(mainframe)
    entry.grid(row=i, column=1)
    entries_vars.append(entry)

(superheat_entry, subcool_entry, displacement_entry,
 speed_entry, evap_min_entry, evap_max_entry,
 cond_min_entry, cond_max_entry) = entries_vars

# Pulsante per calcolare
calc_button = ttk.Button(mainframe, text="Calculate and Save", command=run_calculation)
calc_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

root.mainloop()
