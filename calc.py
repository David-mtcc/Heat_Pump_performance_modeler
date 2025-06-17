# calc.py
from CoolProp.CoolProp import PropsSI
import numpy as np
import pandas as pd

# Parametri di efficienza di default
ETA_MOTOR = 0.90         # efficienza del motore elettrico

def volumetric_efficiency(ratio_compression):
    if ratio_compression < 1.5:
        return 0.3  # oppure addirittura 0.1
    PR_opt = 2.5
    eta_max = 0.92
    curvature = 0.05  # più alto = curva più stretta
    eta_v = eta_max - curvature * (ratio_compression - PR_opt) ** 2
    return max(0.3, min(eta_v, 1.0))

def eta_isentropic_empiric(ratio_compression):
    # Parametri empirici (modifica se vuoi calibrare)
    a = 0.75
    b = -0.15
    c = 0.05

    eta = a + b * ratio_compression + c * ratio_compression**2

    # Limiti fisici
    if eta > 1.0:
        eta = 1.0
    elif eta < 0.5:
        eta = 0.5
    return eta

def calculate_heating_power(refrigerant, T_evap, T_cond, superheat, subcool, displacement_cc, speed_rps):
    
    T_evap_K = T_evap + 273.15
    T_cond_K = T_cond + 273.15

    h1 = PropsSI('H', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    s1 = PropsSI('S', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    h2s = PropsSI('H', 'S', s1, 'T', T_cond_K, refrigerant)
    h3 = PropsSI('H', 'T', T_cond_K - subcool, 'Q', 0, refrigerant)

    # Calcolo rapporto di compressione
    p1 = PropsSI('P', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    p2 = PropsSI('P', 'T', T_cond_K, 'Q', 1, refrigerant)
    ratio_compression = p2 / p1

    eta_isentropic = eta_isentropic_empiric(ratio_compression)
    eta_volumetric = volumetric_efficiency(ratio_compression)

    h2 = h1 + (h2s - h1) / eta_isentropic

    displacement_m3 = displacement_cc * 1e-6
    vol_flow = displacement_m3 * speed_rps * eta_volumetric

    rho = PropsSI('D', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    m_dot = vol_flow * rho

    q_cond = h2 - h3
    Q_dot = q_cond * m_dot
    return Q_dot

def build_heating_map(refrigerant, superheat, subcool, displacement_cc, speed_rps, T_evap_min, T_evap_max, T_cond_min, T_cond_max):
    evaps = np.arange(T_evap_min, T_evap_max + 1)
    conds = np.arange(T_cond_min, T_cond_max + 1)
    heating_map = pd.DataFrame(index=conds, columns=evaps, dtype=float)
    heating_map.index.name = 'T_cond (°C)'
    heating_map.columns.name = 'T_evap (°C)'
    for T_cond in conds:
        for T_evap in evaps:
            heating_map.at[T_cond, T_evap] = calculate_heating_power(
                refrigerant, T_evap, T_cond,
                superheat, subcool,
                displacement_cc, speed_rps
            )
    return heating_map

def calculate_electrical_power(refrigerant, T_evap, T_cond, superheat, subcool, displacement_cc, speed_rps):

    T_evap_K = T_evap + 273.15
    T_cond_K = T_cond + 273.15

    h1 = PropsSI('H', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    s1 = PropsSI('S', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    h2s = PropsSI('H', 'S', s1, 'T', T_cond_K, refrigerant)
    h3 = PropsSI('H', 'T', T_cond_K - subcool, 'Q', 0, refrigerant)

    # Calcolo rapporto di compressione
    p1 = PropsSI('P', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    p2 = PropsSI('P', 'T', T_cond_K, 'Q', 1, refrigerant)
    ratio_compression = p2 / p1

    eta_isentropic = eta_isentropic_empiric(ratio_compression)
    eta_volumetric = volumetric_efficiency(ratio_compression)
    
    h2 = h1 + (h2s - h1) / eta_isentropic


    displacement_m3 = displacement_cc * 1e-6
    vol_flow = displacement_m3 * speed_rps * eta_volumetric

    rho = PropsSI('D', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    m_dot = vol_flow * rho
    w_comp = (h2s - h1) / eta_isentropic

    P_shaft = m_dot * w_comp

    P_elec = P_shaft / ETA_MOTOR

    return P_elec

def build_electric_power_map(refrigerant, superheat, subcool, displacement_cc, speed_rps, T_evap_min, T_evap_max, T_cond_min, T_cond_max):
    evaps = np.arange(T_evap_min, T_evap_max + 1)
    conds = np.arange(T_cond_min, T_cond_max + 1)
    electric_power_map = pd.DataFrame(index=conds, columns=evaps, dtype=float)
    electric_power_map.index.name = 'T_cond (°C)'
    electric_power_map.columns.name = 'T_evap (°C)'
    for T_cond in conds:
        for T_evap in evaps:
            electric_power_map.at[T_cond, T_evap] = calculate_electrical_power(
                refrigerant, T_evap, T_cond,
                superheat, subcool,
                displacement_cc, speed_rps
            )
    return electric_power_map