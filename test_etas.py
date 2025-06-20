import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

# Esempio: punti dell'utente per efficienza isoentropica o volumetrica
x_points = np.array([0, 4, 7, 10])
y_points = np.array([0.4, 0.85, 0.6, 0.25])

# Fit polinomiale di 3° grado (puoi cambiare grado)
degree = 5
coeffs = np.polyfit(x_points, y_points, degree)

# Valori da plottare
x_fit = np.linspace(0, 10, 200)
y_fit = np.polyval(coeffs, x_fit)

# Plot
plt.figure(figsize=(8, 4))
plt.plot(x_fit, y_fit, label=f'Poly fit (deg={degree})')
plt.scatter(x_points, y_points, color='red', zorder=5, label='Input points')
plt.title("Polynomial Fit of Efficiency")
plt.xlabel("Compression Ratio")
plt.ylabel("Efficiency")
plt.ylim(0, 1.2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()