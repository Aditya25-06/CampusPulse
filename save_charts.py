"""Saves every chart as a PNG into the charts/ folder.  Run: python save_charts.py"""
import os
from analysis import PlacementData, ChartMaker

os.makedirs("charts", exist_ok=True)
maker = ChartMaker(PlacementData())
for i, (name, func) in enumerate(maker.catalog().items(), start=1):
    file = f"charts/{i:02d}_{name.split('(')[0].strip().replace(' ', '_').replace('%', 'pct')}.png"
    func(size=(7, 4.2)).savefig(file, dpi=130)
    print("saved", file)
