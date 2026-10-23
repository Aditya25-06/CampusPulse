"""
data_generator.py
Creates a sample (random) placement dataset using only numpy + pandas.
Run:  python data_generator.py      ->  data/placement_data.csv
"""
import os
import numpy as np
import pandas as pd


class DataGenerator:
    """Generates fake but realistic student placement records."""

    DEPARTMENTS = ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil", "MBA"]
    # company: (min package, max package) in LPA
    COMPANIES = {"TCS": (3.5, 4.5), "Infosys": (3.6, 4.8), "Wipro": (3.5, 4.5),
                 "Cognizant": (4.0, 5.0), "Accenture": (4.5, 7.0), "Deloitte": (6.0, 9.0),
                 "L&T": (4.5, 7.5), "Bosch": (5.0, 8.0), "Amazon": (14.0, 32.0),
                 "Microsoft": (16.0, 38.0), "Google": (20.0, 45.0)}
    BOOST = {"CSE": 0.9, "IT": 0.8, "ECE": 0.4, "EEE": 0.2, "Mechanical": 0.0, "Civil": -0.2, "MBA": 0.3}
    DREAM = ["Amazon", "Microsoft", "Google"]
    MID = ["Accenture", "Deloitte", "L&T", "Bosch"]
    MASS = ["TCS", "Infosys", "Wipro", "Cognizant"]

    def __init__(self, n=600, seed=42):
        self.n = n
        self.rng = np.random.default_rng(seed)

    def generate(self):
        r, n = self.rng, self.n
        dept = r.choice(self.DEPARTMENTS, n, p=[0.24, 0.16, 0.16, 0.10, 0.12, 0.08, 0.14])
        year = r.choice([2022, 2023, 2024, 2025], n)
        cgpa = np.clip(r.normal(7.4, 1.0, n), 5.0, 9.9).round(2)
        backlogs = r.choice([0, 1, 2, 3], n, p=[0.70, 0.17, 0.08, 0.05])
        intern = r.choice([0, 1, 2, 3], n, p=[0.35, 0.37, 0.20, 0.08])
        projects = r.choice([0, 1, 2, 3, 4, 5], n)
        aptitude = np.clip(r.normal(65, 14, n) + (cgpa - 7.4) * 5, 20, 100).round(0)
        comm = np.clip(r.normal(64, 15, n), 20, 100).round(0)
        tech = np.clip(r.normal(60, 16, n) + (cgpa - 7.4) * 4, 15, 100).round(0)

        # hidden rule that decides who gets placed
        z = (-6.9 + 0.6 * cgpa + 0.012 * aptitude + 0.01 * comm + 0.015 * tech
             + 0.35 * intern + 0.12 * projects - 0.55 * backlogs
             + np.array([self.BOOST[d] for d in dept]) + r.normal(0, 0.5, n))
        placed = r.random(n) < 1 / (1 + np.exp(-z))

        company, package = [], []
        for i in range(n):
            if not placed[i]:
                company.append("Not Placed"); package.append(0.0); continue
            strength = (cgpa[i] - 5) / 5 * 0.5 + tech[i] / 100 * 0.3 + aptitude[i] / 100 * 0.2
            if strength > 0.68 and dept[i] in ("CSE", "IT", "ECE") and r.random() < 0.5:
                pool = self.DREAM
            elif strength > 0.55:
                pool = self.MID + self.MASS
            else:
                pool = self.MASS
            c = r.choice(pool)
            lo, hi = self.COMPANIES[c]
            company.append(c); package.append(round(float(r.uniform(lo, hi)), 2))

        return pd.DataFrame({
            "StudentID": [f"STU{1000 + i}" for i in range(n)],
            "Department": dept, "BatchYear": year, "CGPA": cgpa, "Backlogs": backlogs,
            "Internships": intern, "Projects": projects, "Aptitude": aptitude,
            "Communication": comm, "Technical": tech,
            "Placed": np.where(placed, "Yes", "No"), "Company": company, "Package": package})


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = DataGenerator().generate()
    df.to_csv("data/placement_data.csv", index=False)
    print(f"Saved {len(df)} student records to data/placement_data.csv")
    print(df.head())
