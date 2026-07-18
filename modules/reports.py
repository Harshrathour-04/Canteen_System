from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
import csv
from connection import connect

class Reports:
    def __init__(self, parent):
        self.running = True  
        self.frame = Frame(parent, bg="#F8FAFC")
        self.frame.pack(fill=BOTH, expand=True)

        self.date_var = StringVar()

        # Header
        Label(self.frame, text="Sales Reports", font=("Segoe UI", 24, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 20))

        # --- Filter Section ---
        filter_card = Frame(self.frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        filter_card.pack(fill=X, pady=(0, 20))
        
        ff = Frame(filter_card, bg="white")
        ff.pack(pady=20, padx=20, fill=X)
        
        Label(ff, text="Filter by Date (YYYY-MM-DD):", font=("Segoe UI", 12, "bold"), bg="white", fg="#0F172A").pack(side=LEFT, padx=(0, 10))
        Entry(ff, textvariable=self.date_var, font=("Segoe UI", 12), width=15, bg="#F8FAFC", relief=SOLID, bd=1).pack(side=LEFT, ipady=4, padx=(0, 15))
        Button(ff, text="🔍 Filter", bg="#064E3B", fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", padx=15, command=self.filter_by_date).pack(side=LEFT, padx=(0, 10))
        Button(ff, text="🔄 Show All", bg="#64748B", fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", padx=15, command=self.fetch_all).pack(side=LEFT, padx=(0, 10))
        
        # Analyze Data Button
        Button(ff, text="📊 Analyze Data", bg="#3B82F6", fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", padx=15, command=self.analyze_data).pack(side=LEFT, padx=(0, 10))
        
        # NEW: Export to CSV Button
        Button(ff, text="💾 Export CSV", bg="#8B5CF6", fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", padx=15, command=self.export_csv).pack(side=LEFT)

        # --- Table Section ---
        table_card = Frame(self.frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        table_card.pack(fill=BOTH, expand=True)
        
        Label(table_card, text="Transaction History", font=("Segoe UI", 16, "bold"), bg="white", fg="#0F172A").pack(anchor="w", padx=20, pady=(20, 10))

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#FFFFFF", foreground="#64748B")

        self.table = ttk.Treeview(table_card, columns=("ID", "Date", "Customer", "Items", "Total", "Status"), show="headings")
        for col in ("ID", "Date", "Customer", "Items", "Total", "Status"):
            self.table.heading(col, text=col.upper())
            self.table.column(col, anchor=CENTER, width=150 if col in ("Items", "Customer") else 100)
            
        self.table.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        self.fetch_all()

    def stop_tasks(self):
        self.running = False

    def populate_table(self, query, params=None):
        try:
            conn = connect()
            cr = conn.cursor()
            if params:
                cr.execute(query, params)
            else:
                cr.execute(query)
            rows = cr.fetchall()
            
            if self.running:
                self.table.delete(*self.table.get_children())
                for row in rows:
                    formatted_row = list(row)
                    if len(formatted_row) > 4:
                        formatted_row[4] = f"₹{formatted_row[4]:.2f}" if isinstance(formatted_row[4], (int, float)) else formatted_row[4]
                    self.table.insert('', END, values=formatted_row)
            conn.close()
        except Exception as e:
            if self.running: messagebox.showerror("Database Error", str(e))

    def fetch_all(self):
        self.date_var.set("")
        query = "SELECT order_id, DATE(order_date), customer_name, items_ordered, grand_total, status FROM sales ORDER BY order_id DESC"
        self.populate_table(query)

    def filter_by_date(self):
        date_str = self.date_var.get()
        if not date_str:
            return messagebox.showerror("Error", "Please enter a date")
            
        query = "SELECT order_id, DATE(order_date), customer_name, items_ordered, grand_total, status FROM sales WHERE DATE(order_date) = %s ORDER BY order_id DESC"
        self.populate_table(query, (date_str,))

    def export_csv(self):
        """Exports the current table data to a CSV file."""
        records = self.table.get_children()
        if not records:
            return messagebox.showinfo("No Data", "There is no data to export.")
            
        # Ask user where to save the file
        file_path = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Report As"
        )
        
        if not file_path:
            return # User cancelled the save dialog
            
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the column headers first
                writer.writerow(["Order ID", "Date", "Customer Name", "Items Ordered", "Grand Total", "Status"])
                
                # Write the actual data
                for row_id in records:
                    row_data = self.table.item(row_id)['values']
                    writer.writerow(row_data)
                    
            messagebox.showinfo("Success", f"Data exported successfully to\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def analyze_data(self):
        """Generates a visual data analytics chart of sales performance."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            conn = connect()
            cr = conn.cursor()
            cr.execute("SELECT DATE(order_date), SUM(grand_total) FROM sales GROUP BY DATE(order_date) ORDER BY DATE(order_date) ASC")
            data = cr.fetchall()
            conn.close()
            
            if not data:
                return messagebox.showinfo("No Data", "Not enough sales data to analyze.")
                
            dates = [str(row[0]) for row in data]
            totals = [float(row[1]) for row in data]
            
            chart_win = Toplevel(self.frame)
            chart_win.title("Data Analytics - Sales Performance")
            chart_win.geometry("700x500")
            chart_win.configure(bg="white")
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(dates, totals, color="#10B981", edgecolor="#047857")
            ax.set_title("Total Revenue by Date", fontsize=14, fontweight="bold", color="#0F172A")
            ax.set_xlabel("Date", fontsize=11, fontweight="bold")
            ax.set_ylabel("Revenue (₹)", fontsize=11, fontweight="bold")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=chart_win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=20, pady=20)
            
        except ImportError:
            messagebox.showerror("Missing Library", "Please run 'pip install matplotlib' in your terminal to generate data visualizations.")
        except Exception as e:
            if self.running: messagebox.showerror("Error", str(e))