from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from connection import connect, resource_path
from datetime import date

class Dashboard:
    def __init__(self, parent):
        self.running = True
        self.frame = Frame(parent, bg="#F8FAFC")
        self.frame.pack(fill=BOTH, expand=True)
        
        # Header
        Label(self.frame, text="Welcome to your Dashboard", font=("Segoe UI", 24, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 5))
        Label(self.frame, text="Here is a summary of your canteen's performance today.", font=("Segoe UI", 12), bg="#F8FAFC", fg="#64748B").pack(anchor="w", pady=(0, 20))

        # Stats Cards
        stats_frame = Frame(self.frame, bg="#F8FAFC")
        stats_frame.pack(fill=X, pady=10)
        
        # List to prevent Tkinter garbage collection of images
        self.dash_icons = [] 
        
        # CHANGED: We now save the returned label into variables so we can update them dynamically
        self.lbl_total_orders = self.create_card(stats_frame, "TOTAL ORDERS", "0", "#3B82F6", "totalorders.png")
        self.lbl_todays_sales = self.create_card(stats_frame, "TODAY'S SALES", "₹0.00", "#10B981", "todaysales.png")
        self.lbl_pending = self.create_card(stats_frame, "PENDING QUEUE", "0", "#F59E0B", "pending.png")
        self.lbl_completed = self.create_card(stats_frame, "COMPLETED", "0", "#8B5CF6", "completed.png")

        # Table
        Label(self.frame, text="Recent Transactions", font=("Segoe UI", 16, "bold"), bg="#F8FAFC").pack(anchor="w", pady=(20, 10))
        
        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#FFFFFF", foreground="#64748B")

        self.table = ttk.Treeview(self.frame, columns=("ID", "Customer", "Items", "Amount", "Status"), show="headings", height=10)
        for col in ("ID", "Customer", "Items", "Amount", "Status"):
            self.table.heading(col, text=col.upper())
            self.table.column(col, anchor=CENTER)
        self.table.pack(fill=BOTH, expand=True)

        # Fetch the data when dashboard loads
        self.fetch_recent_transactions()
        
        # ADDED: Fetch the live metrics right when the screen opens
        self.update_metrics()

    def create_card(self, parent, title, val, color, icon_filename):
        card = Frame(parent, bg="white", highlightbackground="#E2E8F0", highlightthickness=1, width=200, height=100)
        card.pack(side=LEFT, padx=(0, 20), pady=10)
        card.pack_propagate(False)
        
        # Pack the Icon (Right Side)
        try:
            img = Image.open(resource_path(f"asserts/icons/{icon_filename}")).resize((45, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.dash_icons.append(photo) 
            
            icon_label = Label(card, image=photo, bg="white")
            icon_label.image = photo  
            icon_label.pack(side=RIGHT, padx=15)
        except Exception as e:
            print(f"DEBUG: Could not load {icon_filename} in dashboard: {e}")

        # Pack the Text Frame (Left Side)
        text_frame = Frame(card, bg="white")
        text_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        Label(text_frame, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#64748B").pack(anchor="w")
        
        # CHANGED: Create the value label, pack it, and RETURN it so we can change the text later
        val_label = Label(text_frame, text=val, font=("Segoe UI", 20, "bold"), bg="white", fg=color)
        val_label.pack(anchor="w", pady=(5,0))
        
        return val_label
        
    def update_metrics(self):
        try:
            # Get today's date formatted as YYYY-MM-DD
            today = date.today().strftime('%Y-%m-%d')
            
            conn = connect()
            cr = conn.cursor()
            
            # 1. Total Orders Today (Using %s for MySQL)
            cr.execute("SELECT COUNT(*) FROM sales WHERE order_date LIKE %s", (f"{today}%",))
            total_orders = cr.fetchone()[0] or 0
            
            # 2. Today's Sales (Only count completed/paid orders)
            cr.execute("SELECT SUM(grand_total) FROM sales WHERE order_date LIKE %s AND status = 'Paid'", (f"{today}%",))
            todays_sales = cr.fetchone()[0] or 0.0
            
            # 3. Pending Queue Today
            cr.execute("SELECT COUNT(*) FROM sales WHERE order_date LIKE %s AND status = 'Pending'", (f"{today}%",))
            pending_queue = cr.fetchone()[0] or 0
            
            # 4. Completed Today
            cr.execute("SELECT COUNT(*) FROM sales WHERE order_date LIKE %s AND status = 'Paid'", (f"{today}%",))
            completed = cr.fetchone()[0] or 0
            
            # Inject the fetched numbers directly into the Tkinter labels
            self.lbl_total_orders.config(text=str(total_orders))
            self.lbl_todays_sales.config(text=f"₹{todays_sales:.2f}")
            self.lbl_pending.config(text=str(pending_queue))
            self.lbl_completed.config(text=str(completed))
            
            conn.close()
        except Exception as e:
            print(f"DEBUG Dashboard Metrics Error: {e}")

    def fetch_recent_transactions(self):
        try:
            conn = connect()
            cr = conn.cursor()
            # Fetching the 10 most recent orders from the sales table
            cr.execute("SELECT order_id, customer_name, total_items, grand_total, status FROM sales ORDER BY order_id DESC LIMIT 10")
            rows = cr.fetchall()
            
            if self.running:
                self.table.delete(*self.table.get_children())
                for row in rows:
                    formatted_row = list(row)
                    # Add currency symbol to the amount
                    if isinstance(formatted_row[3], (int, float)):
                        formatted_row[3] = f"₹{formatted_row[3]:.2f}"
                    self.table.insert('', END, values=formatted_row)
            conn.close()
        except Exception as e:
            print(f"DEBUG Dashboard Table Error: {e}")

    def stop_tasks(self):
        self.running = False