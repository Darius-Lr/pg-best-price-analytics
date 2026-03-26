import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import ctypes


from random_search import load_data, random_search_material

# =========================
# LOAD DATA
# =========================

df = load_data("Project 2 Data.xlsx")


try:
    best_calendaristic_price = pd.read_excel("Best_Calendaristic_price.xlsx")
    theoretical_best = pd.read_excel("Theoretical_Best_Combinations_S3.xlsx")
except FileNotFoundError:
    best_calendaristic_price = pd.DataFrame()
    theoretical_best = pd.DataFrame()


materials = df['Material Description'].dropna().unique().tolist()


# =========================
# CLASA PENTRU BUTOANE ROTUNJITE
# =========================

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=210, height=40, radius=20, bg_color="#212121",
                 btn_color="#3a3a3a", active_color="#4a4a4a", text_color="white"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.command = command
        self.btn_color = btn_color
        self.active_color = active_color
        self.text_color = text_color
        self.radius = radius
        self.text = text
        self.width = width
        self.height = height

        # bind mouse events
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.draw(self.btn_color)

    def draw(self, color):
        self.delete("all")
        x1 = 0
        y1 = 0
        x2 = self.width
        y2 = self.height
        r = self.radius
        points = [
            x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r,
            x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1,
            y1 + r, x1, y1
        ]
        self.create_polygon(points, fill=color, smooth=True)
        self.create_text(self.width / 2, self.height / 2, text=self.text, fill=self.text_color,
                         font=("Segoe UI", 11, "bold"))

    def on_enter(self, event):
        self.config(cursor="hand2")
        self.draw(self.active_color)

    def on_leave(self, event):
        self.draw(self.btn_color)

    def on_press(self, event):
        self.draw("#2a2a2a")

    def on_release(self, event):
        self.draw(self.active_color)
        if self.command:
            self.command()

    def update_bg(self, new_bg):
        self.config(bg=new_bg)
        self.draw(self.btn_color)


# =========================
# FUNCTII GRAFICE INTEGRATE IN GUI
# =========================


def clear_plot():
    for widget in plot_frame.winfo_children():
        widget.destroy()



def get_colors():
    if dark_mode == True:
        bg_color = '#1e1e1e'
        fg_color = 'white'
    else:
        bg_color = 'white'
        fg_color = 'black'

    return bg_color, fg_color



def calculate_price_impact(df, material):
    data = df[df['Material Description'] == material]


    if data.empty:
        return


    avg_feed = data['Feedstock Price'].mean()
    avg_conv = data['Conversion Price'].mean()
    avg_trans = data['Transport Price'].mean()
    total = avg_feed + avg_conv + avg_trans

    feed_pct = (avg_feed / total) * 100
    conv_pct = (avg_conv / total) * 100
    trans_pct = (avg_trans / total) * 100

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)

    ax.pie([feed_pct, conv_pct, trans_pct], labels=['Feedstock', 'Conversion', 'Transport'], autopct='%1.1f%%',
           textprops={'color': fg_color})
    ax.set_title(f"Price Structure - {material}", color=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def compare_all_models(df, material, best_calendaristic_price, theoretical_best):
    from random_search import random_search_material

    data = df[df['Material Description'] == material]
    if data.empty:
        status_text.set("No data for selected material.")
        return


    real = best_calendaristic_price[best_calendaristic_price['Material Description'] == material]

    theo = theoretical_best[theoretical_best['Material Description'] == material]


    results1, best_random, results2 = random_search_material(df, material, n_iter=2000)

    if real.empty or theo.empty or best_random is None:
        status_text.set("Missing data for comparison.")
        return

    real_price = real['Calculated Price'].min()
    theo_price = theo['Theoretical Best Final Price'].min()
    random_price = best_random['Total Synthetic Price']


    if theo_price > real_price:
        theo_price = real_price

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(8, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    bars = ax.bar(
        ['Real Best', 'Theoretical Best', 'Random Search'],
        [real_price, theo_price, random_price],
        color=['#3498db', '#2ecc71', '#f39c12']
    )


    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom',
                color=fg_color)

    ax.set_title(f"Model Comparison\n{material}", color=fg_color)
    ax.tick_params(colors=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def plot_supplier_comparison(df, material):
    data = df[df['Material Description'] == material]

    if data.empty:
        status_text.set("No data found.")
        return

    base = data.iloc[0]

    m_type = base['Material Type']
    m_sub = base['Material Sub Type']
    plant = base['Plant']


    filtered = df[
        (df['Material Type'] == m_type) &
        (df['Material Sub Type'] == m_sub) &
        (df['Plant'] == plant)
        ].copy()

    if filtered.empty:
        status_text.set("No comparable suppliers.")
        return


    best_per_supplier = (
        filtered.groupby('Supplier')['Calculated Price']
        .min()
        .reset_index()
        .sort_values('Calculated Price')
    )

    if best_per_supplier.empty:
        status_text.set("No supplier data.")
        return

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    import matplotlib.pyplot as plt
    cmap = plt.cm.get_cmap('tab20', len(best_per_supplier))


    colors = []
    for i in range(len(best_per_supplier)):
        colors.append(cmap(i))

    bars = ax.bar(
        best_per_supplier['Supplier'].astype(str),
        best_per_supplier['Calculated Price'],
        color=colors
    )


    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{height:.2f}',
            ha='center',
            va='bottom',
            color=fg_color,
            fontsize=9
        )

    ax.set_title(
        f"Best Price per Supplier (Real Scenario)\n{material}",
        color=fg_color
    )

    ax.set_ylabel("Price", color=fg_color)
    ax.tick_params(axis='x', rotation=45, colors=fg_color)
    ax.tick_params(axis='y', colors=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def plot_total_price_trend(df, material):
    data = df[df['Material Description'] == material].copy()

    if data.empty:
        status_text.set("No data available.")
        return

    data['Date'] = pd.to_datetime(data['Final Price Month'])
    data = data.sort_values('Date')

    monthly = data.groupby('Date')['Calculated Price'].mean().reset_index()

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(9, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    ax.plot(monthly['Date'], monthly['Calculated Price'],
            marker='o', linewidth=2)

    ax.set_title(f"Total Price Evolution\n{material}", color=fg_color)
    ax.set_xlabel("Date", color=fg_color)
    ax.set_ylabel("Price", color=fg_color)
    ax.tick_params(axis='x', rotation=45, colors=fg_color)
    ax.tick_params(axis='y', colors=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def plot_component_trends(df, material):
    data = df[df['Material Description'] == material].copy()
    if data.empty:
        status_text.set("No data available.")
        return

    data['Date'] = pd.to_datetime(data['Final Price Month'])
    data = data.sort_values(by='Date').reset_index(drop=True)

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(10, 8), dpi=100)
    fig.patch.set_facecolor(bg_color)

    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=fg_color)
        ax.grid(alpha=0.2)

    feed = data.groupby('Date')['Feedstock Price'].mean().reset_index()
    ax1.plot(feed['Date'], feed['Feedstock Price'], marker='o', linewidth=2)
    ax1.set_title("Feedstock Trend", color=fg_color)

    conv = data.groupby('Date')['Conversion Price'].mean().reset_index()
    ax2.plot(conv['Date'], conv['Conversion Price'], marker='s', linewidth=2)
    ax2.set_title("Conversion Trend", color=fg_color)

    trans = data.groupby('Date')['Transport Price'].mean().reset_index()


    has_transport = False
    for val in trans['Transport Price']:
        if pd.notna(val) and val > 0:
            has_transport = True

    if has_transport == True:
        trans['Transport Price'] = trans['Transport Price'].replace(0, None)


        trans['diff'] = trans['Transport Price'].diff().abs()
        threshold = trans['Transport Price'].mean() * 0.8
        trans.loc[trans['diff'] > threshold, 'Transport Price'] = None

    ax3.plot(
        trans['Date'],
        trans['Transport Price'],
        marker='^',
        linewidth=2
    )
    ax3.set_title("Transport Trend", color=fg_color)
    ax3.tick_params(axis='x', rotation=45)

    fig.suptitle(f"Component Trends (Separated)\n{material}",
                 color=fg_color, fontsize=12)

    fig.tight_layout(rect=[0, 0, 1, 0.96])

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def gui_plot_random_search(results_df, material):
    clear_plot()
    bg_color, fg_color = get_colors()
    fig = Figure(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    ax.hist(results_df['Total Synthetic Price'], bins=50, color='#1f538d', edgecolor='black', alpha=0.7,
            label='Combinatii Simulate')

    best_price = results_df['Total Synthetic Price'].min()
    avg_price = results_df['Total Synthetic Price'].mean()
    worst_price = results_df['Total Synthetic Price'].max()

    ax.axvline(best_price, color='#2fa572', linestyle='-', linewidth=3, label=f'Best: {best_price:.2f}')
    ax.axvline(avg_price, color='#e5b524', linestyle='--', linewidth=2, label=f'Avg: {avg_price:.2f}')
    ax.axvline(worst_price, color='#d32727', linestyle=':', linewidth=2, label=f'Worst: {worst_price:.2f}')

    ax.set_title(f'{material}\nDistributia Combinatiilor Sintetice', color=fg_color)
    ax.set_xlabel('Pret Total Sintetic', color=fg_color)
    ax.set_ylabel('Frecventa', color=fg_color)
    ax.tick_params(colors=fg_color)
    ax.legend(facecolor=bg_color, edgecolor=fg_color, labelcolor=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def get_valid_color(c_name, fallback="#4fa8d1"):
    try:
        clean_name = str(c_name).strip().replace(" ", "").lower()
        mcolors.to_rgba(clean_name)
        return clean_name
    except ValueError:
        return fallback



def plot_color_analysis(df, material):
    data = df[df['Material Description'] == material]

    if data.empty:
        status_text.set("No data found.")
        return

    base = data.iloc[0]

    filtered = df[
        (df['Material Type'] == base['Material Type']) &
        (df['Material Sub Type'] == base['Material Sub Type'])
        ].copy()

    if filtered.empty:
        status_text.set("No comparable materials.")
        return

    best_per_color = (
        filtered.groupby('Color')['Calculated Price']
        .min()
        .reset_index()
        .sort_values(by='Calculated Price')
    )

    if best_per_color.empty:
        status_text.set("No color data.")
        return

    clear_plot()
    bg_color, fg_color = get_colors()

    fig = Figure(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)


    colors = []
    for c in best_per_color['Color']:
        colors.append(get_valid_color(c))

    bars = ax.bar(
        range(len(best_per_color)),
        best_per_color['Calculated Price'],
        color=colors
    )

    ax.set_xticks(range(len(best_per_color)))
    ax.set_xticklabels(best_per_color['Color'], rotation=30, color=fg_color)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom',
                color=fg_color)

    ax.set_title(f"Best Price per Color (Real Data)\n{material}", color=fg_color)
    ax.set_ylabel("Price", color=fg_color)
    ax.tick_params(axis='y', colors=fg_color)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def set_titlebar_color(window, dark=True):
    try:
        window.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

        if dark == True:
            value = ctypes.c_int(1)
        else:
            value = ctypes.c_int(0)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value),
                                                   ctypes.sizeof(value))
    except Exception:
        pass


# =========================
# APP WINDOW SETUP
# =========================
root = tk.Tk()
root.title("P&G Optimization Dashboard")
root.geometry("1200x800")
root.configure(bg="#1e1e1e")

set_titlebar_color(root, dark=True)

style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox", fieldbackground="#2d2d2d", background="#2d2d2d", foreground="white")

# =========================
# LEFT PANEL
# =========================
sidebar = tk.Frame(root, bg="#212121", width=250)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

title = tk.Label(sidebar, text="Optimization Tool", bg="#212121", fg="white", font=("Segoe UI", 16, "bold"))
title.pack(pady=30)

buttons = []

# =========================
# RIGHT PANEL
# =========================
main_area = tk.Frame(root, bg="#1e1e1e")
main_area.pack(side="right", expand=True, fill="both")

info_frame = tk.Frame(main_area, bg="#1e1e1e")
info_frame.pack(pady=10, fill="x", padx=20)

fields = [
    "Material Type", "Material Sub Type", "Material Description", "Plant",
    "Supplier", "BU", "UoM", "Incoterm",
    "Grammage", "Color", "Material Status", "SP Low"
]
info_vars = {}


for i in range(len(fields)):
    field = fields[i]
    info_vars[field] = tk.StringVar(value="N/A")
    row = i // 4
    col = i % 4

    pair_frame = tk.Frame(info_frame, bg="#1e1e1e")
    pair_frame.grid(row=row, column=col, sticky="w", padx=10, pady=4)

    lbl = tk.Label(pair_frame, text=f"{field}:", fg="white", bg="#1e1e1e", font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left")

    val = tk.Label(pair_frame, textvariable=info_vars[field], fg="#4fa8d1", bg="#1e1e1e", font=("Segoe UI", 9))
    val.pack(side="left", padx=(5, 0))

for c in range(4):
    info_frame.grid_columnconfigure(c, weight=1)

dark_mode = True

label = tk.Label(main_area, text="Select Material:", bg="#1e1e1e", fg="white", font=("Segoe UI", 12))
label.pack(pady=10)

selected_material = tk.StringVar()
dropdown = ttk.Combobox(main_area, textvariable=selected_material, values=materials, width=50)
dropdown.pack(pady=5)

status_text = tk.StringVar()
status_text.set("Ready")
status_label = tk.Label(main_area, textvariable=status_text, bg="#1e1e1e", fg="#2fa572", font=("Segoe UI", 10))
status_label.pack(pady=5)

plot_frame = tk.Frame(main_area, bg="#1e1e1e")
plot_frame.pack(fill="both", expand=True, padx=20, pady=10)


# =========================
# BUTTON FUNCTIONS
# =========================

def toggle_theme():
    global dark_mode
    # light mode switch
    if dark_mode == True:
        root.configure(bg="white")
        main_area.configure(bg="white")
        sidebar.configure(bg="#e0e0e0")
        title.configure(bg="#e0e0e0", fg="black")
        status_label.configure(bg="white", fg="#008000")
        label.configure(bg="white", fg="black")
        info_frame.configure(bg="white")
        plot_frame.configure(bg="white")

        for pair in info_frame.winfo_children():
            pair.configure(bg="white")
            for widget in pair.winfo_children():
                widget.configure(bg="white")
                if isinstance(widget, tk.Label):
                    if "bold" in widget.cget("font"):
                        widget.configure(fg="black")
                    else:
                        widget.configure(fg="#1f538d")

        for btn in buttons:
            btn.update_bg("#e0e0e0")

        set_titlebar_color(root, dark=False)
        dark_mode = False

    #dark mode switch
    else:
        root.configure(bg="#1e1e1e")
        main_area.configure(bg="#1e1e1e")
        sidebar.configure(bg="#212121")
        title.configure(bg="#212121", fg="white")
        status_label.configure(bg="#1e1e1e", fg="#2fa572")
        label.configure(bg="#1e1e1e", fg="white")
        info_frame.configure(bg="#1e1e1e")
        plot_frame.configure(bg="#1e1e1e")

        for pair in info_frame.winfo_children():
            pair.configure(bg="#1e1e1e")
            for widget in pair.winfo_children():
                widget.configure(bg="#1e1e1e")
                if isinstance(widget, tk.Label):
                    if "bold" in widget.cget("font"):
                        widget.configure(fg="white")
                    else:
                        widget.configure(fg="#4fa8d1")

        for btn in buttons:
            btn.update_bg("#212121")

        set_titlebar_color(root, dark=True)
        dark_mode = True

    clear_plot()
    status_text.set("Theme changed. Please re-run the chart.")


def update_material_info(event=None):
    material = selected_material.get()
    if not material:
        return

    row = df[df['Material Description'] == material].iloc[0]

    for field in fields:
        val = row.get(field, "N/A")
        if pd.notna(val):
            info_vars[field].set(str(val))
        else:
            info_vars[field].set("N/A")

    clear_plot()


dropdown.bind("<<ComboboxSelected>>", update_material_info)


# button commands
def run_impact():
    if selected_material.get():
        status_text.set("Calculating price structure...")
        root.update()
        calculate_price_impact(df, selected_material.get())
        status_text.set("Done.")


def run_trends():
    if selected_material.get():
        status_text.set("Generating trends...")
        root.update()
        plot_component_trends(df, selected_material.get())
        status_text.set("Done.")


def run_compare():
    if selected_material.get():
        status_text.set("Comparing models...")
        root.update()
        compare_all_models(df, selected_material.get(), best_calendaristic_price, theoretical_best)
        status_text.set("Done.")


def run_random():
    material = selected_material.get()
    if material:
        status_text.set("Running random search...")
        root.update()
        results, _, _ = random_search_material(df, material, n_iter=2000)
        if results is not None:
            gui_plot_random_search(results, material)
            status_text.set("Random search completed.")


def run_color_analysis():
    if selected_material.get():
        status_text.set("Analyzing color prices...")
        root.update()
        plot_color_analysis(df, selected_material.get())
        status_text.set("Done.")


def run_supplier_analysis():
    if selected_material.get():
        status_text.set("Analyzing suppliers...")
        root.update()
        plot_supplier_comparison(df, selected_material.get())
        status_text.set("Done.")


def run_total_price_trend():
    if selected_material.get():
        status_text.set("Analyzing total price...")
        root.update()
        plot_total_price_trend(df, selected_material.get())
        status_text.set("Done.")


# function to easily add a button to the sidebar
def add_rounded_button(text, command):
    btn = RoundedButton(sidebar, text=text, command=command, bg_color="#212121", btn_color="#3a3a3a",
                        active_color="#505050")
    btn.pack(pady=12)
    buttons.append(btn)


# all buttons
add_rounded_button("Price Structure", run_impact)
add_rounded_button("Component Trends", run_trends)
add_rounded_button("Compare Models", run_compare)
add_rounded_button("Random Search", run_random)
add_rounded_button("Color Analysis", run_color_analysis)
add_rounded_button("Supplier Comparison", run_supplier_analysis)
add_rounded_button("Total Price Trend", run_total_price_trend)

# theme button bottom
theme_btn = RoundedButton(sidebar, text="🌙 / ☀️ Toggle Theme", command=toggle_theme, bg_color="#212121",
                          btn_color="#3a3a3a", active_color="#505050")
theme_btn.pack(side="bottom", pady=40)
buttons.append(theme_btn)

# footer
footer = tk.Label(root, text="P&G Internship Project - Optimization Tool\n© Lare Claudiu Darius. All rights reserved",
                  bg="#1e1e1e", fg="gray",
                  font=("Segoe UI", 9), justify="left")
footer.pack(side="bottom", pady=20)

root.mainloop()
