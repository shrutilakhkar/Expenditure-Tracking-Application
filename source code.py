import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sqlite3
from matplotlib import pyplot as plt
import time

def create_db():
    conn = sqlite3.connect("expenditure.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenditure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        quantity INTEGER,
        cost REAL,
        total REAL
    )
    """)
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect("expenditure.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenditure")
    data = cursor.fetchall()
    conn.close()
    return data

def add_to_db(item, quantity, cost, total):
    conn = sqlite3.connect("expenditure.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenditure (item, quantity, cost, total) VALUES (?, ?, ?, ?)",
                   (item, quantity, cost, total))
    conn.commit()
    conn.close()

def reset_data():
    result = messagebox.askyesno("Reset Confirmation", "Are you sure you want to reset all data?")
    if result:
        conn = sqlite3.connect("expenditure.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenditure")
        conn.commit()
        conn.close()

        item_list.clear()
        refresh_display_animated()

        messagebox.showinfo("Reset", "All data has been reset successfully.")

create_db()

root = tk.Tk()
root.geometry("1000x600")
root.title("Expenditure Tracker")
root.configure(background="#f6f6f6")

item_list = []

def add_item():
    item = item_txt.get()
    quantity = quantity_txt.get()
    cost = cost_txt.get()

    if not item or not quantity or not cost:
        messagebox.showwarning("Input Error", "Please fill in all fields!")
        return

    try:
        total = int(quantity) * float(cost)
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter valid numeric values for Quantity and Cost!")
        return

    single_item = {"Item": item, "Quantity": quantity, "Cost": cost, "Total Amount": total}
    item_list.append(single_item)

    add_to_db(item, quantity, cost, total)

    refresh_display_animated()

def refresh_display_animated():
    for widget in frame2.winfo_children():
        widget.destroy()

    header = ["Item", "Quantity", "Cost", "Total Amount"]
    for i, col in enumerate(header):
        header_label = ttk.Label(frame2, text=col, font=("Arial", 14, "bold"), width=20, anchor="center")
        header_label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        header_label.after(i * 200, header_label.config, {"foreground": "black"})

    data = fetch_data()
    for i, row in enumerate(data, start=1):
        item_lbl = ttk.Label(frame2, text=f"{row[1]}", font=("Arial", 12), width=20, anchor="center")
        item_lbl.grid(row=i, column=0, padx=5, pady=5, sticky="w")
        item_lbl.after(i * 100, item_lbl.config, {"foreground": "black"})

        quantity_lbl = ttk.Label(frame2, text=f"{row[2]}", font=("Arial", 12), width=20, anchor="center")
        quantity_lbl.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        quantity_lbl.after(i * 100, quantity_lbl.config, {"foreground": "black"})

        cost_lbl = ttk.Label(frame2, text=f"{row[3]}", font=("Arial", 12), width=20, anchor="center")
        cost_lbl.grid(row=i, column=2, padx=5, pady=5, sticky="w")
        cost_lbl.after(i * 100, cost_lbl.config, {"foreground": "black"})

        total_lbl = ttk.Label(frame2, text=f"{row[4]}", font=("Arial", 12), width=20, anchor="center")
        total_lbl.grid(row=i, column=3, padx=5, pady=5, sticky="w")
        total_lbl.after(i * 100, total_lbl.config, {"foreground": "black"})

    frame2.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def clear_item():
    item_txt.delete(0, "end")
    quantity_txt.delete(0, "end")
    cost_txt.delete(0, "end")

def analyse():
    if not item_list:
        messagebox.showwarning("No Data", "Please add some items to analyze!")
        return

    df = pd.DataFrame(item_list)
    items = df['Item']
    total = df['Total Amount']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(items, total, color='royalblue', width=0.4)

    ax.set_ylabel("Cost of items")
    ax.set_xlabel("Items Purchased")
    ax.set_title("Expenditure Tracker Analysis")
    plt.xticks(rotation=45, ha='right')

    def animate_bars():
        for bar in bars:
            height = bar.get_height()
            bar.set_height(0)
            for i in range(0, int(height), 2):
                bar.set_height(i)
                plt.draw()
                plt.pause(0.01)

    animate_bars()
    plt.tight_layout()
    plt.show()

def export_to_csv():
    if not item_list:
        messagebox.showwarning("No Data", "No items to export!")
        return

    filename = "expenditure_report.csv"

    # Fetch data from the database for consistency
    data = fetch_data()

    # Prepare the data to be exported
    export_data = []
    for row in data:
        export_data.append({
            "Item": row[1],
            "Quantity": row[2],
            "Cost": row[3],
            "Total Amount": row[4]
        })

    # Convert to DataFrame for exporting
    df = pd.DataFrame(export_data)

    try:
        df.to_csv(filename, index=False)
        messagebox.showinfo("Export Successful", f"Data exported successfully to {filename}")
    except Exception as e:
        messagebox.showerror("Export Failed", f"An error occurred: {e}")

header_frame = tk.Frame(root, bg="#FF6F61")
header_frame.pack(fill=tk.X, pady=10)

title_lbl = ttk.Label(header_frame, text="Expenditure Tracker", font=("Arial", 20, "bold"), background="#FF6F61", foreground="white", padding=(10, 5))
title_lbl.pack(pady=10)

content_frame = tk.Frame(root, bg="#f6f6f6")
content_frame.pack(fill=tk.BOTH, expand=True)

item_lbl = ttk.Label(content_frame, text="Item:", font=("Arial", 15), background="#f6f6f6")
item_lbl.pack(pady=(20, 5))
item_txt = ttk.Entry(content_frame, font=("Arial", 12), width=30)
item_txt.pack()

quantity_lbl = ttk.Label(content_frame, text="Quantity:", font=("Arial", 15), background="#f6f6f6")
quantity_lbl.pack(pady=(20, 5))
quantity_txt = ttk.Entry(content_frame, font=("Arial", 12), width=30)
quantity_txt.pack()

cost_lbl = ttk.Label(content_frame, text="Cost Per Unit:", font=("Arial", 15), background="#f6f6f6")
cost_lbl.pack(pady=(20, 5))
cost_txt = ttk.Entry(content_frame, font=("Arial", 12), width=30)
cost_txt.pack()

frame1 = ttk.Frame(content_frame)
frame1.pack(pady=10)

add_btn = ttk.Button(frame1, text="Add Item", command=add_item, width=20)
add_btn.pack(side=tk.LEFT, padx=10)

clear_btn = ttk.Button(frame1, text="Clear", command=clear_item, width=20)
clear_btn.pack(side=tk.RIGHT, padx=10)

reset_btn = ttk.Button(content_frame, text="Reset All Data", command=reset_data, width=20, style="TButton")
reset_btn.pack(pady=10)

display_lbl = ttk.Label(content_frame, text="Expenses", font=("Arial", 15), background="#f6f6f6")
display_lbl.pack(pady=(20, 5))

canvas = tk.Canvas(content_frame)
canvas.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")

frame2 = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame2, anchor="nw")
canvas.config(yscrollcommand=scrollbar.set)

analyse_btn = ttk.Button(content_frame, text="Analyse", command=analyse, width=20)
analyse_btn.pack(pady=10)

export_btn = ttk.Button(content_frame, text="Export to CSV", command=export_to_csv, width=20)
export_btn.pack(pady=10)

footer_frame = tk.Frame(root, bg="#FF6F61")
footer_frame.pack(fill=tk.X, pady=10)

footer_lbl = ttk.Label(footer_frame, text=" 2025 Expenditure Tracker - By Shruti Lakhkar ", font=("Arial", 10, "italic"), background="#FF6F61", foreground="white")
footer_lbl.pack(pady=5)

refresh_display_animated()

root.mainloop()
