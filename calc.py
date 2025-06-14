# calc.py
from CoolProp.CoolProp import PropsSI
import numpy as np
import pandas as pd

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
    return df
