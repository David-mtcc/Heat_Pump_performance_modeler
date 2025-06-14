# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import calc  # importiamo il modulo di calcolo

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

    df_map = calc.build_heating_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        T_evap_min, T_evap_max,
        T_cond_min, T_cond_max
    )

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

refrigerant_var = tk.StringVar(value='R134a')

ttk.Label(mainframe, text="Select refrigerant:").grid(row=0, column=0, sticky=tk.W)
refrigerant_combo = ttk.Combobox(mainframe, textvariable=refrigerant_var, state="readonly")
refrigerant_combo['values'] = ('R134a', 'R32', 'R290','R410A','R454B','R407C','R744')
refrigerant_combo.grid(row=0, column=1)

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

calc_button = ttk.Button(mainframe, text="Calculate and Save", command=run_calculation)
calc_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

root.mainloop()
