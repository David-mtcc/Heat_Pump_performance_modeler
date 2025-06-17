# test_eta_v.py
from calc import volumetric_efficiency, eta_isentropic_empiric

ratios = [1.2, 1.5, 2, 3, 5, 8, 10]

for r in ratios:
    eta_v = volumetric_efficiency(r)
    print(f"Rapporto di compressione: {r:.1f} -> Efficienza volumetrica: {eta_v:.3f}")

for dp in ratios:
    eta_s = eta_isentropic_empiric(dp)
    print(f"Rapporto di compressione: {dp:.1f} -> Efficienza isentropica: {eta_s:.3f}")