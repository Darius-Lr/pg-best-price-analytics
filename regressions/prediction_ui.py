import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd

from prediction_engine import (
    MODEL_EXPLANATIONS,
    MODEL_OPTIONS,
    MODEL_SELECTOR_LABELS,
    build_prediction_table,
)


DISPLAY_COLUMNS = [
    "Material Type",
    "Material Sub Type",
    "Material Description",
    "Plant",
    "Supplier",
    "Status",
    "Model",
    "Last Actual Month",
    "Months Requested",
    "Training Months Before Cleaning",
    "Training Months Used",
    "Garbage Removed",
    "Predicted Final Price",
    "Actual Final Price",
    "Difference",
    "Abs Difference",
    "Percent Error",
    "Removed Rows",
]


class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P&G Price Prediction")
        self.root.geometry("1500x820")

        self.file_path_var = tk.StringVar()
        self.model_var = tk.StringVar(value="ridge")
        self.history_mode_var = tk.StringVar(value="all")
        self.months_var = tk.StringVar(value="6")
        self.ignore_garbage_var = tk.BooleanVar(value=False)
        self.summary_var = tk.StringVar(
            value="Incarca un fisier Excel, alege modelul si ruleaza predictia."
        )

        self._build_layout()

    def _build_layout(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        title_label = ttk.Label(
            container,
            text="Predictii pe grup pentru fisiere Excel",
            style="Title.TLabel",
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            container,
            text=(
                "Alege modelul, cate luni din urma sa foloseasca si daca sa elimine valorile garbage."
            ),
        )
        subtitle_label.pack(anchor="w", pady=(4, 14))

        controls_frame = ttk.Frame(container)
        controls_frame.pack(fill="x")

        file_frame = ttk.LabelFrame(controls_frame, text="Fisier Excel", style="Section.TLabelframe")
        file_frame.pack(fill="x", pady=(0, 10))

        ttk.Entry(file_frame, textvariable=self.file_path_var).pack(
            side="left", fill="x", expand=True, padx=(10, 8), pady=10
        )
        ttk.Button(file_frame, text="Upload Excel", command=self.select_file).pack(
            side="left", padx=(0, 10), pady=10
        )

        options_frame = ttk.Frame(container)
        options_frame.pack(fill="x", pady=(0, 10))

        model_frame = ttk.LabelFrame(options_frame, text="Model", style="Section.TLabelframe")
        model_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        for model_key in MODEL_OPTIONS:
            option_frame = ttk.Frame(model_frame)
            option_frame.pack(fill="x", padx=10, pady=6, anchor="w")

            ttk.Radiobutton(
                option_frame,
                text=MODEL_SELECTOR_LABELS[model_key],
                value=model_key,
                variable=self.model_var,
            ).pack(anchor="w")

            ttk.Label(
                option_frame,
                text=MODEL_EXPLANATIONS[model_key],
                wraplength=520,
                justify="left",
            ).pack(anchor="w", padx=(24, 0), pady=(2, 0))

        history_frame = ttk.LabelFrame(
            options_frame,
            text="Istoric folosit",
            style="Section.TLabelframe",
        )
        history_frame.pack(side="left", fill="both", expand=True)

        ttk.Radiobutton(
            history_frame,
            text="Foloseste toate lunile disponibile",
            value="all",
            variable=self.history_mode_var,
            command=self.toggle_months_entry,
        ).pack(anchor="w", padx=10, pady=(10, 6))

        custom_frame = ttk.Frame(history_frame)
        custom_frame.pack(anchor="w", padx=10, pady=(0, 10))

        ttk.Radiobutton(
            custom_frame,
            text="Foloseste ultimele",
            value="custom",
            variable=self.history_mode_var,
            command=self.toggle_months_entry,
        ).pack(side="left")

        self.months_entry = ttk.Entry(custom_frame, width=8, textvariable=self.months_var)
        self.months_entry.pack(side="left", padx=6)
        ttk.Label(custom_frame, text="luni").pack(side="left")

        cleanup_frame = ttk.LabelFrame(
            container,
            text="Curatare date",
            style="Section.TLabelframe",
        )
        cleanup_frame.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(
            cleanup_frame,
            text="Elimina valorile garbage din Final Price inainte de antrenare",
            variable=self.ignore_garbage_var,
        ).pack(anchor="w", padx=10, pady=10)

        actions_frame = ttk.Frame(container)
        actions_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(actions_frame, text="Calculeaza predictii", command=self.run_predictions).pack(
            side="left"
        )
        ttk.Label(actions_frame, textvariable=self.summary_var).pack(side="left", padx=(12, 0))

        table_frame = ttk.Frame(container)
        table_frame.pack(fill="both", expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=DISPLAY_COLUMNS, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tree.xview
        )
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        for column in DISPLAY_COLUMNS:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=150, anchor="w")

        self.tree.column("Status", width=240)
        self.tree.column("Material Description", width=220)
        self.tree.column("Removed Rows", width=260)

        self.toggle_months_entry()

    def toggle_months_entry(self):
        state = "normal" if self.history_mode_var.get() == "custom" else "disabled"
        self.months_entry.configure(state=state)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Alege fisierul Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )
        if file_path:
            self.file_path_var.set(file_path)

    def run_predictions(self):
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("Fisier lipsa", "Alege mai intai un fisier Excel.")
            return

        months_back = None
        if self.history_mode_var.get() == "custom":
            raw_months = self.months_var.get().strip()
            if not raw_months.isdigit():
                messagebox.showerror("Valoare invalida", "Numarul de luni trebuie sa fie un numar intreg.")
                return
            months_back = int(raw_months)
            if months_back < 2:
                messagebox.showerror("Valoare invalida", "Numarul de luni trebuie sa fie cel putin 2.")
                return

        try:
            results = build_prediction_table(
                file_path=file_path,
                model_key=self.model_var.get(),
                months_back=months_back,
                ignore_garbage=self.ignore_garbage_var.get(),
            )
        except Exception as exc:
            messagebox.showerror("Eroare", str(exc))
            return

        self.populate_table(results)

        ok_count = int((results["Status"] == "OK").sum()) if not results.empty else 0
        skipped_count = len(results) - ok_count
        self.summary_var.set(
            f"Grupuri procesate: {len(results)} | Predictii generate: {ok_count} | Sarite: {skipped_count}"
        )

    def populate_table(self, results):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        if results.empty:
            return

        display_frame = results.copy()

        if "Last Actual Month" in display_frame.columns:
            display_frame["Last Actual Month"] = display_frame["Last Actual Month"].astype(str)

        numeric_columns = [
            "Outlier Lower Bound",
            "Outlier Upper Bound",
            "Feedstock Price",
            "Conversion Price",
            "Transport Price",
            "Actual Final Price",
            "Predicted Final Price",
            "Difference",
            "Abs Difference",
            "Percent Error",
        ]

        for column in numeric_columns:
            if column in display_frame.columns:
                display_frame[column] = display_frame[column].map(self.format_numeric)

        for _, row in display_frame.iterrows():
            values = [row.get(column, "") for column in DISPLAY_COLUMNS]
            self.tree.insert("", "end", values=values)

    @staticmethod
    def format_numeric(value):
        if pd.isna(value):
            return ""
        return f"{float(value):.2f}"


def main():
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
