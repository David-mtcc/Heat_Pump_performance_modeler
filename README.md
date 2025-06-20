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

## Contact
For questions or contributions, please open an issue or submit a pull request.
