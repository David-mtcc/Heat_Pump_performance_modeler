# calc.py
from CoolProp.CoolProp import PropsSI
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, Point

# Parametri di efficienza di default
ETA_MOTOR = 0.90         # efficienza del motore elettrico

def generate_grid_inside_polygon(polygon_points, resolution=1.0):
    """
    Genera una griglia regolare di punti (x, y) all'interno di un poligono 2D.
    :param polygon_points: Lista di tuple [(x1, y1), (x2, y2), ...] che definiscono il poligono.
    :param resolution: Distanza tra i punti della griglia (in unità coordinate, es: °C).
    :return: Lista di tuple [(x, y), ...] interne al poligono.
    """
    poly = Polygon(polygon_points)
    minx, miny, maxx, maxy = poly.bounds

    x_vals = np.arange(minx, maxx + resolution, resolution)
    y_vals = np.arange(miny, maxy + resolution, resolution)

    grid_points = [
        (x, y) for x in x_vals for y in y_vals if poly.contains(Point(x, y))
    ]
    return grid_points


def volumetric_efficiency(ratio_compression, coeffs):
    etav = np.polyval(coeffs, ratio_compression)
    return etav

def eta_isentropic_empiric(ratio_compression, coeffs):
    etas = np.polyval(coeffs, ratio_compression)
    return etas

def refrigerant_cycle_calculation(refrigerant, T_evap, T_cond, superheat, subcool, displacement_cc, speed_rps, volumetric_coeffs, isentropic_coeffs):
    T_evap_K = T_evap + 273.15
    T_cond_K = T_cond + 273.15

    # Stato 1: in aspirazione (vapore surriscaldato)
    h1 = PropsSI('H', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    s1 = PropsSI('S', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    # Stato 2s: scarico isentropico (adiabatico)
    h2s = PropsSI('H', 'S', s1, 'T', T_cond_K, refrigerant)
    # Stato 3: uscita condensatore (liquido sottoraffreddato)
    h3 = PropsSI('H', 'T', T_cond_K - subcool, 'Q', 0, refrigerant)

    # Pressioni per rapporto di compressione
    p1 = PropsSI('P', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    p2 = PropsSI('P', 'T', T_cond_K, 'Q', 1, refrigerant)
    ratio_compression = p2 / p1

    eta_isentropic = eta_isentropic_empiric(ratio_compression, isentropic_coeffs)
    eta_volumetric = volumetric_efficiency(ratio_compression, volumetric_coeffs)

    # Stato 2 reale (tenendo conto dell'efficienza isentropica)
    h2 = h1 + (h2s - h1) / eta_isentropic

    displacement_m3 = displacement_cc * 1e-6  # da cc a m³
    vol_flow = displacement_m3 * speed_rps * eta_volumetric

    rho = PropsSI('D', 'T', T_evap_K + superheat, 'Q', 1, refrigerant)
    m_dot = vol_flow * rho

    q_cond = h2 - h3  # entalpia ceduta al condensatore per kg
    Q_dot = q_cond * m_dot  # potenza termica (W)

    w_comp = (h2s - h1) / eta_isentropic  # lavoro specifico di compressione (J/kg)
    P_shaft = m_dot * w_comp              # potenza al compressore (W)
    P_elec = P_shaft / ETA_MOTOR          # potenza elettrica (W)

    return Q_dot, P_elec

def build_heating_map(refrigerant, superheat, subcool, displacement_cc, speed_rps, points, volumetric_coeffs, isentropic_coeffs):
    import pandas as pd
    # Estraggo le temperature uniche per righe (cond) e colonne (evap) per indicizzare la DataFrame
    evap_temps = sorted(set(p[0] for p in points))
    cond_temps = sorted(set(p[1] for p in points))

    heating_map = pd.DataFrame(index=cond_temps, columns=evap_temps, dtype=float)
    heating_map.index.name = 'T_cond (°C)'
    heating_map.columns.name = 'T_evap (°C)'

    for (T_evap, T_cond) in points:
        Q_dot, _ = refrigerant_cycle_calculation(
            refrigerant, T_evap, T_cond,
            superheat, subcool,
            displacement_cc, speed_rps, volumetric_coeffs, isentropic_coeffs
        )
        heating_map.at[T_cond, T_evap] = Q_dot
    return heating_map

def build_electric_power_map(refrigerant, superheat, subcool, displacement_cc, speed_rps, points, volumetric_coeffs, isentropic_coeffs):
    import pandas as pd
    evap_temps = sorted(set(p[0] for p in points))
    cond_temps = sorted(set(p[1] for p in points))

    electric_power_map = pd.DataFrame(index=cond_temps, columns=evap_temps, dtype=float)
    electric_power_map.index.name = 'T_cond (°C)'
    electric_power_map.columns.name = 'T_evap (°C)'

    for (T_evap, T_cond) in points:
        _ , W_dot = refrigerant_cycle_calculation(
            refrigerant, T_evap, T_cond,
            superheat, subcool,
            displacement_cc, speed_rps, volumetric_coeffs, isentropic_coeffs
        )
        electric_power_map.at[T_cond, T_evap]=W_dot
    return electric_power_map
