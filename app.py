"""
College Placement Analytics System  (Tkinter GUI)
Libraries : numpy, pandas, matplotlib, tkinter   (nothing else!)
Run       : python app.py
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from analysis import PlacementData, ChartMaker, Predictor

# ---------- colours / fonts used everywhere ----------
BG, DARK, PRIMARY = "#F1F5F9", "#1E293B", "#4F46E5"
CARD_COLORS = ["#4F46E5", "#10B981", "#06B6D4", "#F59E0B", "#EF4444"]


class PlacementApp(tk.Tk):
    """Main window.  Every tab is built by its own method."""

    def __init__(self):
        super().__init__()
        self.title("College Placement Analytics System")
        self.geometry("1180x720")
        self.configure(bg=BG)

        self.data = PlacementData()          # object that holds the data
        self.charts = ChartMaker(self.data)  # object that draws charts
        self.predictor = Predictor()         # object that predicts placement
        self.canvases = {}                   # remember chart canvases so we can replace them

        self.setup_style()
        self.build_header()
        self.build_filter_bar()
        self.build_tabs()
        self.refresh_all()

    # ------------------------------------------------------------------ style
    def setup_style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=(18, 8))
        st.map("TNotebook.Tab", background=[("selected", PRIMARY)], foreground=[("selected", "white")])
        st.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=PRIMARY, foreground="white")
        st.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        st.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    # ----------------------------------------------------------------- header
    def build_header(self):
        head = tk.Frame(self, bg=PRIMARY, height=70)
        head.pack(fill="x")
        tk.Label(head, text="🎓  College Placement Analytics System", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=14)
        tk.Label(head, text="Analyse • Visualise • Predict", bg=PRIMARY, fg="#C7D2FE",
                 font=("Segoe UI", 11)).pack(side="right", padx=20)

    def build_filter_bar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=15, pady=(10, 0))
        tk.Label(bar, text="Batch Year:", bg=BG, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.year_var = tk.StringVar(value="All")
        years = ["All"] + [str(y) for y in sorted(self.data.full["BatchYear"].unique())]
        ttk.Combobox(bar, textvariable=self.year_var, values=years, width=8, state="readonly").pack(side="left", padx=(5, 15))
        tk.Label(bar, text="Department:", bg=BG, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.dept_var = tk.StringVar(value="All")
        depts = ["All"] + sorted(self.data.full["Department"].unique())
        ttk.Combobox(bar, textvariable=self.dept_var, values=depts, width=12, state="readonly").pack(side="left", padx=(5, 15))
        ttk.Button(bar, text="Apply Filter", command=self.refresh_all).pack(side="left")
        ttk.Button(bar, text="Reset", command=self.reset_filters).pack(side="left", padx=6)
        self.count_label = tk.Label(bar, text="", bg=BG, fg="#64748B", font=("Segoe UI", 10))
        self.count_label.pack(side="right")

    def build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)
        self.tab_dash = tk.Frame(self.tabs, bg=BG)
        self.tab_charts = tk.Frame(self.tabs, bg=BG)
        self.tab_dept = tk.Frame(self.tabs, bg=BG)
        self.tab_pred = tk.Frame(self.tabs, bg=BG)
        self.tab_rec = tk.Frame(self.tabs, bg=BG)
        for tab, name in [(self.tab_dash, "  Dashboard  "), (self.tab_charts, "  Charts  "),
                          (self.tab_dept, "  Departments & Companies  "),
                          (self.tab_pred, "  Predictor  "), (self.tab_rec, "  Student Records  ")]:
            self.tabs.add(tab, text=name)
        self.build_dashboard()
        self.build_charts_tab()
        self.build_dept_tab()
        self.build_predictor_tab()
        self.build_records_tab()

    # ------------------------------------------------------------ small helpers
    def show_figure(self, key, fig, parent):
        """Put a matplotlib figure inside a Tk frame (replacing the old one)."""
        if key in self.canvases:
            self.canvases[key].get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases[key] = canvas

    def reset_filters(self):
        self.year_var.set("All"); self.dept_var.set("All")
        self.refresh_all()

    # ------------------------------------------------------------- 1. dashboard
    def build_dashboard(self):
        self.card_row = tk.Frame(self.tab_dash, bg=BG)
        self.card_row.pack(fill="x", pady=10)
        self.card_labels = {}
        for i, name in enumerate(["Total Students", "Placed", "Placement %", "Avg Package (LPA)", "Highest Package (LPA)"]):
            card = tk.Frame(self.card_row, bg=CARD_COLORS[i], padx=12, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, text=name, bg=CARD_COLORS[i], fg="white", font=("Segoe UI", 10)).pack()
            val = tk.Label(card, text="0", bg=CARD_COLORS[i], fg="white", font=("Segoe UI", 22, "bold"))
            val.pack()
            self.card_labels[name] = val
        row = tk.Frame(self.tab_dash, bg=BG)
        row.pack(fill="both", expand=True)
        self.dash_left = tk.Frame(row, bg="white"); self.dash_left.pack(side="left", fill="both", expand=True, padx=6)
        self.dash_right = tk.Frame(row, bg="white"); self.dash_right.pack(side="left", fill="both", expand=True, padx=6)

    def update_dashboard(self):
        for name, value in self.data.kpis().items():
            self.card_labels[name].config(text=str(value))
        self.show_figure("d1", self.charts.status_pie(), self.dash_left)
        self.show_figure("d2", self.charts.package_hist(), self.dash_right)

    # ---------------------------------------------------------------- 2. charts
    def build_charts_tab(self):
        top = tk.Frame(self.tab_charts, bg=BG)
        top.pack(fill="x", pady=8)
        tk.Label(top, text="Choose a chart:", bg=BG, font=("Segoe UI", 11, "bold")).pack(side="left", padx=8)
        self.chart_var = tk.StringVar(value="Department Placement %")
        box = ttk.Combobox(top, textvariable=self.chart_var, values=list(self.charts.catalog()),
                           width=30, state="readonly", font=("Segoe UI", 11))
        box.pack(side="left")
        box.bind("<<ComboboxSelected>>", lambda e: self.update_charts_tab())
        ttk.Button(top, text="💾 Save Chart as PNG", command=self.save_chart).pack(side="left", padx=12)
        self.chart_frame = tk.Frame(self.tab_charts, bg="white")
        self.chart_frame.pack(fill="both", expand=True, padx=6, pady=4)

    def update_charts_tab(self):
        maker = self.charts.catalog()[self.chart_var.get()]
        self.current_fig = maker(size=(8.5, 4.6))
        self.show_figure("chart", self.current_fig, self.chart_frame)

    def save_chart(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png")])
        if path:
            self.current_fig.savefig(path, dpi=150)
            messagebox.showinfo("Saved", f"Chart saved to:\n{path}")

    # -------------------------------------------------- 3. departments / companies
    def build_dept_tab(self):
        left = ttk.LabelFrame(self.tab_dept, text=" Department Summary ")
        left.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        cols = ("Department", "Students", "Placed", "Placement %", "Avg Package")
        self.dept_tree = ttk.Treeview(left, columns=cols, show="headings", height=8)
        for c in cols:
            self.dept_tree.heading(c, text=c); self.dept_tree.column(c, width=95, anchor="center")
        self.dept_tree.pack(fill="x", padx=6, pady=6)
        self.dept_chart_frame = tk.Frame(left, bg="white")
        self.dept_chart_frame.pack(fill="both", expand=True, padx=6, pady=6)

        right = ttk.LabelFrame(self.tab_dept, text=" Company Summary ")
        right.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        cols2 = ("Company", "Hired", "Avg Package")
        self.comp_tree = ttk.Treeview(right, columns=cols2, show="headings", height=12)
        for c in cols2:
            self.comp_tree.heading(c, text=c); self.comp_tree.column(c, width=100, anchor="center")
        self.comp_tree.pack(fill="both", expand=True, padx=6, pady=6)

    def fill_tree(self, tree, df, with_index=True):
        tree.delete(*tree.get_children())
        for idx, row in df.iterrows():
            tree.insert("", "end", values=([idx] if with_index else []) + list(row.values))

    def update_dept_tab(self):
        self.fill_tree(self.dept_tree, self.data.dept_summary())
        self.fill_tree(self.comp_tree, self.data.company_summary())
        self.show_figure("dept", self.charts.dept_bar(size=(5.2, 3.0)), self.dept_chart_frame)

    # ------------------------------------------------------------- 4. predictor
    def build_predictor_tab(self):
        left = ttk.LabelFrame(self.tab_pred, text=" Enter Student Details ")
        left.pack(side="left", fill="y", padx=10, pady=10)
        self.sliders = {}
        spec = [("CGPA", 5.0, 10.0, 7.5, 0.1), ("Backlogs", 0, 4, 0, 1), ("Internships", 0, 3, 1, 1),
                ("Projects", 0, 5, 2, 1), ("Aptitude", 20, 100, 65, 1),
                ("Communication", 20, 100, 65, 1), ("Technical", 15, 100, 60, 1)]
        for name, lo, hi, default, step in spec:
            tk.Label(left, text=name, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
            s = tk.Scale(left, from_=lo, to=hi, resolution=step, orient="horizontal", length=300,
                         troughcolor="#C7D2FE", highlightthickness=0, command=lambda v: self.update_prediction())
            s.set(default); s.pack(padx=10)
            self.sliders[name] = s
        right = tk.Frame(self.tab_pred, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.pred_label = tk.Label(right, text="", font=("Segoe UI", 44, "bold"), bg=BG)
        self.pred_label.pack(pady=(30, 0))
        self.pred_msg = tk.Label(right, text="", font=("Segoe UI", 15, "bold"), bg=BG)
        self.pred_msg.pack()
        self.pred_bar = ttk.Progressbar(right, length=420, maximum=100)
        self.pred_bar.pack(pady=15)
        tk.Label(right, text="Suggestions to improve", font=("Segoe UI", 13, "bold"), bg=BG, fg=DARK).pack(pady=(20, 4))
        self.tips_box = tk.Label(right, text="", font=("Segoe UI", 11), bg="#EEF2FF", fg=DARK,
                                 justify="left", anchor="w", padx=15, pady=12, wraplength=480)
        self.tips_box.pack(fill="x", padx=30)

    def update_prediction(self):
        if not hasattr(self, "tips_box"):
            return
        s = {k: v.get() for k, v in self.sliders.items()}
        p = self.predictor.probability(s) * 100
        color, msg = ("#10B981", "High chance of placement ✅") if p >= 70 else \
                     ("#F59E0B", "Moderate chance ⚠️") if p >= 40 else ("#EF4444", "Low chance ❌")
        self.pred_label.config(text=f"{p:.1f}%", fg=color)
        self.pred_msg.config(text=msg, fg=color)
        self.pred_bar["value"] = p
        self.tips_box.config(text="\n".join("➜ " + t for t in self.predictor.tips(s)))

    # --------------------------------------------------------------- 5. records
    def build_records_tab(self):
        top = tk.Frame(self.tab_rec, bg=BG)
        top.pack(fill="x", pady=8)
        tk.Label(top, text="Search (ID / company):", bg=BG, font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)
        self.search_var = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.search_var, width=22)
        e.pack(side="left")
        e.bind("<KeyRelease>", lambda ev: self.update_records())
        tk.Label(top, text="Status:", bg=BG, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(15, 4))
        self.status_var = tk.StringVar(value="All")
        sb = ttk.Combobox(top, textvariable=self.status_var, values=["All", "Placed", "Not Placed"], width=10, state="readonly")
        sb.pack(side="left")
        sb.bind("<<ComboboxSelected>>", lambda ev: self.update_records())
        ttk.Button(top, text="⬇ Export CSV", command=self.export_csv).pack(side="left", padx=15)
        self.rec_count = tk.Label(top, text="", bg=BG, fg="#64748B")
        self.rec_count.pack(side="right", padx=6)
        cols = list(self.data.full.columns)
        frame = tk.Frame(self.tab_rec); frame.pack(fill="both", expand=True)
        self.rec_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.rec_tree.heading(c, text=c); self.rec_tree.column(c, width=90, anchor="center")
        sb_y = ttk.Scrollbar(frame, orient="vertical", command=self.rec_tree.yview)
        self.rec_tree.configure(yscrollcommand=sb_y.set)
        self.rec_tree.pack(side="left", fill="both", expand=True); sb_y.pack(side="right", fill="y")

    def records_view(self):
        d = self.data.df
        if self.status_var.get() != "All":
            d = d[d["Placed"] == ("Yes" if self.status_var.get() == "Placed" else "No")]
        q = self.search_var.get().strip().lower()
        if q:
            d = d[d["StudentID"].str.lower().str.contains(q) | d["Company"].str.lower().str.contains(q)]
        return d

    def update_records(self):
        d = self.records_view()
        self.rec_tree.delete(*self.rec_tree.get_children())
        for _, row in d.head(300).iterrows():
            self.rec_tree.insert("", "end", values=list(row.values))
        self.rec_count.config(text=f"Showing {min(len(d), 300)} of {len(d)} records")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if path:
            self.records_view().to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Saved {len(self.records_view())} records to:\n{path}")

    # ------------------------------------------------------------- refresh all
    def refresh_all(self):
        n = self.data.apply_filter(self.year_var.get(), self.dept_var.get())
        if n == 0:
            messagebox.showwarning("No data", "No records match this filter.")
            return
        self.count_label.config(text=f"{n} students selected")
        self.update_dashboard()
        self.update_charts_tab()
        self.update_dept_tab()
        self.update_prediction()
        self.update_records()


if __name__ == "__main__":
    PlacementApp().mainloop()
