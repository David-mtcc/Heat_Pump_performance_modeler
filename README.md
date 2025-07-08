# Heat Pump Performance Modeler

This project is a heat pump performance model with a Python graphical user interface (Tkinter).  
It calculates heating power, electrical power, and COP maps based on operating parameters and refrigerants.

---

## Requirements

- Python 3.7 or higher  
- [CoolProp](https://github.com/CoolProp/CoolProp)  
- numpy  
- pandas  
- plotly  
- tkinter (usually included with Python)

You can install dependencies easily with:

```bash
pip install CoolProp numpy pandas plotly
```

## How to run
Start the GUI with:

```bash
python gui.py
```
A window will appear for entering parameters and calculating performance maps.
Results (CSV files and interactive HTML plots) will be saved in the ```results``` folder at the root of the project.

## Project Structure
```gui.py```: main graphical user interface using Tkinter

```calc.py```: thermodynamic calculation functions and compressor models

```results.py```: saving results and generating interactive plots

```results/```: folder where output files are saved (auto-created)

---
---
## 📘 Physical and Mathematical Background

This project simulates the **thermal and electrical performance** of a **vapor compression heat pump** across a wide range of operating conditions, defined by the user. The simulation includes calculations of:

- Heating Power Output  
- Electrical Power Consumption  
- Coefficient of Performance (COP)  

It does so by modeling a simplified **thermodynamic cycle** using real refrigerant properties and empirical efficiency correlations. The following sections describe the physical and mathematical principles used in the computation.

---

### 🔧 1. Thermodynamic Cycle Description

The core of the model is based on the **idealized vapor-compression cycle**, which consists of four main processes:

1. **Evaporation** (low pressure, low temperature):  
   The refrigerant absorbs heat and evaporates, entering the compressor as superheated vapor.
   
2. **Compression** (isentropic idealized):  
   The vapor is compressed, increasing its pressure and temperature.

3. **Condensation** (high pressure):  
   The hot vapor releases heat and condenses into liquid.

4. **Expansion** (isenthalpic, not modeled explicitly here):  
   The liquid refrigerant undergoes expansion before re-entering the evaporator.

---

### 🧮 2. Inputs and User-Defined Parameters

The user provides:

- **Refrigerant Type** (e.g., R134a, R290, R410A, etc.)
- **Superheat & Subcooling** (in Kelvin)
- **Compressor Displacement** (in cc/rev)
- **Compressor Speed** (in rev/s)
- **Envelope Polygon**: 8 user-defined points representing (Evaporation Temp °C, Condensation Temp °C)
- **Volumetric Efficiency Curve**: 4 user-defined points for fitting a 4th-degree polynomial
- **Isentropic Efficiency Curve**: same as above

---

### 📈 3. Performance Mapping

For each point within the polygonal envelope, the tool calculates:

#### a. Volumetric Flow Rate
```math
V_{dot} = V_{disp} · n · η_v
```
where:
- $V_{dot}$ is the volumetric flow rate
- $V_{disp}$ is the compressor displacement (m³/rev)
- $n$ is the compressor speed (rev/s)
- $eta_v$ is the volumetric efficiency

#### b. Mass Flow Rate
```math
m_{dot} = V_{dot} · ρ_{inlet}
```
where:
- $m_{dot}$ is the mass flow rate
- $ρ_{inlet}$ is the vapor density at compressor inlet

#### c. Enthalpies and Work

Thermodynamic states are calculated using [CoolProp](https://coolprop.org/):

- `h1`: superheated vapor (evaporator outlet)  
- `h2s`: isentropic outlet after compression  
- `h2`: real outlet after compression (η_s considered)  
- `h3`: subcooled liquid after condenser
with $h2 = h1 + (h2s - h1) / η_s$

#### d. Heating Power (Condenser Output)
```math
Q_{dot_cond} = ṁ · (h2 - h3)
```
#### e. Electrical Power Input
```math
W_{dot_elec} = m_{dot} · (h2s - h1) / (η_s · η_{motor})
```
#### f. Coefficient of Performance (COP)
```math
COP = Q_{dot-cond} / W_{dot-elec}
```
---

### 🧮 4. Efficiency Models

Both **volumetric** and **isentropic** efficiencies are modeled as **4th-degree polynomials** of the **compression ratio**:
```math
r = Compression Ratio = P_{cond} / P_{evap}
```
```math
η_v(r) = a₄r⁴ + a₃r³ + a₂r² + a₁r + a₀
```

The coefficients are estimated via least squares from user-defined points using NumPy's `polyfit()`.

---

### 🔲 5. Discretization and Grid Generation

The working envelope is discretized into a **regular grid of points** `(T_evap, T_cond)` using `shapely`. Only points that lie **inside the polygon** are considered for simulation.

Each valid point undergoes a full thermodynamic simulation. Results are saved as:

- `.csv` files (heating power, electrical power, COP)
- `.html` interactive heatmaps using Plotly

---

### 🔬 6. Software Libraries Used

- [CoolProp](https://coolprop.org/) – thermodynamic properties
- [Tkinter](https://docs.python.org/3/library/tkinter.html) – GUI interface
- [Plotly](https://plotly.com/python/) – interactive plotting
- [NumPy](https://numpy.org/) – numerical computing
- [Pandas](https://pandas.pydata.org/) – data handling
- [Shapely](https://shapely.readthedocs.io/) – polygon geometry and grid generation

---

This model provides a **flexible**, **interactive**, and **accurate** tool for simulating heat pump performance under customizable operating conditions.
