"""
heat_pump_model.py

A CLI tool to compute and map heat pump heating power over grids of evaporation and condensation temperatures,
using compressor displacement and speed to derive mass flow.

Dependencies:
  - CoolProp  (thermodynamic properties)
  - NumPy
  - pandas

Install dependencies via:
  pip install CoolProp numpy pandas

Usage:
  python heat_pump_model.py
"""

import sys
import numpy as np
import pandas as pd
import os

# Try to import CoolProp, provide guidance if missing
try:
    from CoolProp.CoolProp import PropsSI
except ImportError:
    print("Error: CoolProp module not found.")
    print("Please install it with: pip install CoolProp")
    sys.exit(1)


def calculate_heating_power(refrigerant, T_evap, T_cond, superheat, subcool,
                             displacement_cc, speed_rps, eta_isentropic=0.7):
    """
    Calculate absolute heating power for given conditions using compressor parameters.

    Parameters:
      displacement_cc : float, compressor displacement in cm^3 per revolution
      speed_rps       : float, compressor speed in revolutions per second
    """
    # Convert temperatures to Kelvin
    T_evap_K = T_evap + 273.15
    T_cond_K = T_cond + 273.15

    # Define states via CoolProp
    h1 = PropsSI('H', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    s1 = PropsSI('S', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    h2s = PropsSI('H', 'S', s1, 'T', T_cond_K, refrigerant)
    h2 = h1 + (h2s - h1) / eta_isentropic
    h3 = PropsSI('H', 'T', T_cond_K - subcool, 'Q', 0, refrigerant)

    # Compressor volumetric flow: convert cc to m^3
    displacement_m3 = displacement_cc * 1e-6
    vol_flow = displacement_m3 * speed_rps  # m^3/s

    # Suction density
    rho = PropsSI('D', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    m_dot = vol_flow * rho  # kg/s

    # Condenser heat duty per kg
    q_cond = h2 - h3  # J/kg
    Q_dot = q_cond * m_dot  # W
    return Q_dot


def build_heating_map(refrigerant, superheat, subcool, displacement_cc, speed_rps,
                      T_evap_min, T_evap_max, T_cond_min, T_cond_max):
    evaps = np.arange(T_evap_min, T_evap_max + 1)
    conds = np.arange(T_cond_min, T_cond_max + 1)
    df = pd.DataFrame(index=conds, columns=evaps, dtype=float)
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


def main():
    refrigerants = ['R134a', 'R32', 'R290']
    print("Available refrigerants:")
    for i, r in enumerate(refrigerants, start=1):
        print(f"  {i}. {r}")

    try:
        choice = int(input("Select refrigerant (number): "))
        refrigerant = refrigerants[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

    try:
        superheat = float(input("Superheat (K): "))
        subcool = float(input("Subcooling (K): "))
        displacement_cc = float(input("Compressor displacement (cc per rev): "))
        speed_rps = float(input("Compressor speed (rev per second): "))
        T_evap_min = float(input("Min evaporation temp (°C): "))
        T_evap_max = float(input("Max evaporation temp (°C): "))
        T_cond_min = float(input("Min condensation temp (°C): "))
        T_cond_max = float(input("Max condensation temp (°C): "))
    except ValueError:
        print("Please enter numeric values.")
        sys.exit(1)

    df_map = build_heating_map(
        refrigerant, superheat, subcool,
        displacement_cc, speed_rps,
        T_evap_min, T_evap_max, T_cond_min, T_cond_max
    )

    print("\nAbsolute heating power map (W):")
    print(df_map)

     # Ottengo il percorso della cartella dove si trova il file Python
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')

    # Creo la cartella results nella stessa directory del file
    os.makedirs(results_dir, exist_ok=True)

    output_file = os.path.join(results_dir, 'heating_power_map.csv')
    df_map.to_csv(output_file)
    print(f"Results saved to {output_file}")

if __name__ == '__main__':
    main()
