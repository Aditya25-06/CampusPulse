# 🎓 College Placement Analytics System (Tkinter Edition)

A simple desktop app that analyses campus placement data, draws charts and predicts a student's chance of placement.

**Only uses:** `numpy`, `pandas`, `matplotlib`, `tkinter` — written with **classes & objects**.

## Run
```bash
pip install -r requirements.txt        # numpy, pandas, matplotlib  (tkinter ships with Python)
python data_generator.py               # optional - creates data/placement_data.csv
python app.py                          # start the application
```
> Linux only: if tkinter is missing, run `sudo apt install python3-tk`.

## Files
| File | What it does |
|------|--------------|
| `data_generator.py` | class `DataGenerator` – creates 600 random student records |
| `analysis.py` | classes `PlacementData` (summaries), `ChartMaker` (charts), `Predictor` (placement chance) |
| `app.py` | class `PlacementApp(tk.Tk)` – the GUI with 5 tabs |
| `save_charts.py` | saves all charts as PNG in `charts/` |

## Tabs
Dashboard • Charts (9 charts, save as PNG) • Departments & Companies • Predictor (sliders) • Student Records (search, filter, export CSV)

The top bar filters everything by Batch Year and Department.
