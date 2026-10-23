"""Renders console outputs as images for the report."""
import subprocess
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from analysis import PlacementData, Predictor
pd.set_option("display.width", 130)

def term(text, name, title):
    lines = text.rstrip().split("\n"); h = 0.25 * len(lines) + 0.9
    fig = plt.figure(figsize=(10, h), facecolor="#0F172A")
    fig.text(0.02, 1 - 0.35 / h, "● ● ●   " + title, color="#94A3B8", family="monospace", fontsize=10, va="center")
    fig.text(0.02, 1 - 0.7 / h, "\n".join(lines), color="#A7F3D0", family="monospace", fontsize=9.5, va="top", linespacing=1.35)
    fig.savefig(f"screenshots/{name}.png", dpi=140, facecolor="#0F172A"); plt.close()

out = subprocess.run(["python3", "data_generator.py"], capture_output=True, text=True).stdout
term("$ python data_generator.py\n" + out, "out_01_data_generation", "Terminal - data_generator.py")
d = PlacementData()
t = "$ python -c \"from analysis import *\"  # KPIs and summaries\n\nKPIs\n"
t += "\n".join(f"  {k:<22}: {v}" for k, v in d.kpis().items())
t += "\n\nDEPARTMENT SUMMARY\n" + d.dept_summary().to_string()
t += "\n\nTOP RECRUITERS\n" + d.company_summary().head(5).to_string()
term(t, "out_02_summaries", "Terminal - analysis output")
p = Predictor()
s = dict(CGPA=8.2, Backlogs=0, Internships=2, Projects=3, Aptitude=75, Communication=70, Technical=78)
w = dict(CGPA=5.8, Backlogs=2, Internships=0, Projects=1, Aptitude=45, Communication=50, Technical=40)
t = "$ python -c \"Predictor().probability(student)\"\n\nStrong student  : " + str(s) + f"\n  -> chance = {p.probability(s)*100:.1f}%\n\nWeak student    : " + str(w) + f"\n  -> chance = {p.probability(w)*100:.1f}%\n  -> tips   = {p.tips(w)}"
term(t, "out_03_prediction", "Terminal - Predictor class")
