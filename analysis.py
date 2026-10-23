"""
analysis.py
Classes that do the number work (PlacementData), draw charts (ChartMaker)
and predict placement chance (Predictor).  Uses only numpy, pandas, matplotlib.
"""
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


class PlacementData:
    """Holds the dataset and gives summaries (an 'object' that knows its data)."""

    def __init__(self, path="data/placement_data.csv"):
        self.full = pd.read_csv(path)
        self.df = self.full.copy()          # currently filtered data

    # ---------- filtering ----------
    def apply_filter(self, year="All", dept="All"):
        d = self.full
        if year != "All":
            d = d[d["BatchYear"] == int(year)]
        if dept != "All":
            d = d[d["Department"] == dept]
        self.df = d
        return len(d)

    def placed(self):
        return self.df[self.df["Placed"] == "Yes"]

    # ---------- summaries ----------
    def kpis(self):
        p = self.placed()
        total = len(self.df)
        return {
            "Total Students": total,
            "Placed": len(p),
            "Placement %": round(len(p) / total * 100, 1) if total else 0,
            "Avg Package (LPA)": round(float(p["Package"].mean()), 2) if len(p) else 0,
            "Highest Package (LPA)": round(float(p["Package"].max()), 2) if len(p) else 0,
        }

    def dept_summary(self):
        g = self.df.groupby("Department")
        out = pd.DataFrame({"Students": g.size(),
                            "Placed": g["Placed"].apply(lambda s: (s == "Yes").sum())})
        out["Placement %"] = (out["Placed"] / out["Students"] * 100).round(1)
        out["Avg Package"] = self.placed().groupby("Department")["Package"].mean().round(2)
        return out.fillna(0).sort_values("Placement %", ascending=False)

    def company_summary(self):
        return (self.placed().groupby("Company")["Package"]
                .agg(Hired="count", AvgPackage="mean").round(2)
                .sort_values("Hired", ascending=False))

    def year_summary(self):
        g = self.df.groupby("BatchYear")
        out = pd.DataFrame({"Students": g.size(),
                            "Placed": g["Placed"].apply(lambda s: (s == "Yes").sum())})
        out["Placement %"] = (out["Placed"] / out["Students"] * 100).round(1)
        return out

    def cgpa_band_summary(self):
        bands = pd.cut(self.df["CGPA"], [0, 6, 7, 8, 9, 10], right=False,
                       labels=["<6", "6-7", "7-8", "8-9", "9+"])
        flag = (self.df["Placed"] == "Yes").astype(int)
        return (flag.groupby(bands, observed=False).mean() * 100).round(1)


class ChartMaker:
    """Creates matplotlib Figure objects (they are shown inside Tkinter)."""
    COLORS = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

    def __init__(self, data: PlacementData):
        self.data = data

    def _fig(self, size=(5.4, 3.6)):
        fig = Figure(figsize=size, dpi=100)
        ax = fig.add_subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig, ax

    def status_pie(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        p = len(self.data.placed()); t = len(self.data.df)
        ax.pie([p, t - p], labels=["Placed", "Not Placed"], autopct="%1.1f%%", startangle=90,
               colors=["#10B981", "#EF4444"], wedgeprops=dict(width=0.45))
        ax.set_title("Placement Status", fontweight="bold")
        fig.tight_layout(); return fig

    def dept_bar(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        d = self.data.dept_summary()
        bars = ax.bar(d.index, d["Placement %"], color=self.COLORS[0])
        ax.bar_label(bars, fmt="%.0f%%", fontsize=8)
        ax.set_ylim(0, 100); ax.set_ylabel("Placement %")
        ax.set_title("Department-wise Placement %", fontweight="bold")
        ax.tick_params(axis="x", labelrotation=30, labelsize=8)
        fig.tight_layout(); return fig

    def package_hist(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        ax.hist(self.data.placed()["Package"], bins=20, color=self.COLORS[1], edgecolor="white")
        ax.set_xlabel("Package (LPA)"); ax.set_ylabel("Students")
        ax.set_title("Package Distribution", fontweight="bold")
        fig.tight_layout(); return fig

    def dept_package(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        d = self.data.dept_summary()
        mx = self.data.placed().groupby("Department")["Package"].max().reindex(d.index).fillna(0)
        x = np.arange(len(d))
        ax.bar(x - 0.2, d["Avg Package"], 0.4, label="Average", color=self.COLORS[0])
        ax.bar(x + 0.2, mx, 0.4, label="Highest", color=self.COLORS[3])
        ax.set_xticks(x); ax.set_xticklabels(d.index, rotation=30, fontsize=8)
        ax.set_ylabel("LPA"); ax.legend(); ax.set_title("Average vs Highest Package", fontweight="bold")
        fig.tight_layout(); return fig

    def top_companies(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        c = self.data.company_summary().head(8).iloc[::-1]
        bars = ax.barh(c.index, c["Hired"], color=self.COLORS[2])
        ax.bar_label(bars, fontsize=8); ax.set_xlabel("Students hired")
        ax.set_title("Top Recruiters", fontweight="bold")
        fig.tight_layout(); return fig

    def year_trend(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        y = self.data.year_summary()
        ax.plot(y.index, y["Placement %"], marker="o", lw=3, color=self.COLORS[0])
        for x_, v in zip(y.index, y["Placement %"]):
            ax.annotate(f"{v}%", (x_, v + 2), ha="center", fontsize=8)
        ax.set_xticks(list(y.index)); ax.set_ylim(0, 100); ax.set_ylabel("Placement %")
        ax.set_title("Year-wise Placement Trend", fontweight="bold")
        fig.tight_layout(); return fig

    def cgpa_band(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        b = self.data.cgpa_band_summary()
        bars = ax.bar(b.index.astype(str), b.values, color=self.COLORS[5])
        ax.bar_label(bars, fmt="%.0f%%", fontsize=8)
        ax.set_ylim(0, 110); ax.set_xlabel("CGPA band"); ax.set_ylabel("Placement %")
        ax.set_title("Placement % by CGPA", fontweight="bold")
        fig.tight_layout(); return fig

    def cgpa_scatter(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        p = self.data.placed()
        ax.scatter(p["CGPA"], p["Package"], c=self.COLORS[4], alpha=0.6, s=18)
        ax.set_xlabel("CGPA"); ax.set_ylabel("Package (LPA)")
        ax.set_title("CGPA vs Package", fontweight="bold")
        fig.tight_layout(); return fig

    def skill_bar(self, size=(5.4, 3.6)):
        fig, ax = self._fig(size)
        cols = ["Aptitude", "Communication", "Technical"]
        d = self.data.df
        yes = d[d.Placed == "Yes"][cols].mean(); no = d[d.Placed == "No"][cols].mean()
        x = np.arange(3)
        ax.bar(x - 0.2, yes, 0.4, label="Placed", color="#10B981")
        ax.bar(x + 0.2, no, 0.4, label="Not Placed", color="#EF4444")
        ax.set_xticks(x); ax.set_xticklabels(cols); ax.set_ylim(0, 100); ax.legend()
        ax.set_title("Average Skill Scores", fontweight="bold")
        fig.tight_layout(); return fig

    # name -> method  (used by the dropdown in the app)
    def catalog(self):
        return {"Placement Status (Pie)": self.status_pie, "Department Placement %": self.dept_bar,
                "Package Distribution": self.package_hist, "Avg vs Highest Package": self.dept_package,
                "Top Recruiters": self.top_companies, "Year-wise Trend": self.year_trend,
                "CGPA Band Analysis": self.cgpa_band, "CGPA vs Package": self.cgpa_scatter,
                "Skill Comparison": self.skill_bar}


class Predictor:
    """Very simple scoring model: weights x student values -> probability (0-1)."""
    WEIGHTS = {"CGPA": 0.6, "Backlogs": -0.55, "Internships": 0.35, "Projects": 0.12,
               "Aptitude": 0.012, "Communication": 0.01, "Technical": 0.015}
    BIAS = -6.5

    def probability(self, s: dict) -> float:
        z = self.BIAS + sum(self.WEIGHTS[k] * s[k] for k in self.WEIGHTS)
        return float(1 / (1 + np.exp(-z)))

    def tips(self, s: dict):
        t = []
        if s["CGPA"] < 7: t.append("Raise your CGPA above 7.0.")
        if s["Backlogs"] > 0: t.append("Clear all backlogs.")
        if s["Internships"] == 0: t.append("Do at least one internship.")
        if s["Projects"] < 2: t.append("Build 2-3 good projects.")
        if s["Aptitude"] < 60: t.append("Practise aptitude questions daily.")
        if s["Communication"] < 60: t.append("Join mock interviews / GDs.")
        if s["Technical"] < 60: t.append("Revise DSA, DBMS and OS.")
        return t or ["Great profile! Keep practising and apply widely."]
