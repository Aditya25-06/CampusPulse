"""Helper: opens each tab and saves a screenshot (used to make the report images)."""
import subprocess, sys
from app import PlacementApp
app = PlacementApp()
app.geometry("1180x720+0+0")
shots = [("01_dashboard", 0, None), ("02_charts_dept", 1, "Department Placement %"),
         ("03_charts_trend", 1, "Year-wise Trend"), ("04_charts_cgpa", 1, "CGPA vs Package"),
         ("05_departments_companies", 2, None), ("06_predictor", 3, None), ("07_records", 4, None)]
queue = list(shots)

def step():
    if not queue:
        app.destroy(); return
    name, tab, chart = queue.pop(0)
    app.tabs.select(tab)
    if chart:
        app.chart_var.set(chart); app.update_charts_tab()
    app.update_idletasks(); app.update()
    app.after(700, lambda: (subprocess.run(["import", "-window", "root", "-crop", "1180x720+0+0", f"screenshots/{name}.png"]), step()))
app.after(1000, step)
app.mainloop()
