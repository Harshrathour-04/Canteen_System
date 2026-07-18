from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from connection import connect, resource_path

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
        
        self.create_card(stats_frame, "TOTAL ORDERS", "10", "#3B82F6", "totalorders.png")
        self.create_card(stats_frame, "TODAY'S SALES", "₹0.00", "#10B981", "todaysales.png")
        self.create_card(stats_frame, "PENDING QUEUE", "0", "#F59E0B", "pending.png")
        self.create_card(stats_frame, "COMPLETED", "10", "#8B5CF6", "completed.png")

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

    def create_card(self, parent, title, val, color, icon_filename):
        card = Frame(parent, bg="white", highlightbackground="#E2E8F0", highlightthickness=1, width=200, height=100)
        card.pack(side=LEFT, padx=(0, 20), pady=10)
        card.pack_propagate(False)
        
        # 1. Pack the Icon FIRST (Right Side)
        try:
            img = Image.open(resource_path(f"asserts/icons/{icon_filename}")).resize((45, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # The absolutely bulletproof way to prevent Tkinter garbage collection:
            icon_label = Label(card, image=photo, bg="white")
            icon_label.image = photo  # <--- THIS LINE is the magic fix!
            icon_label.pack(side=RIGHT, padx=15)
        except Exception as e:
            # If the image fails to load, this will print the exact reason to your VS Code terminal
            print(f"DEBUG: Could not load {icon_filename} in dashboard: {e}")

        # 2. Pack the Text Frame SECOND (Left Side)
        text_frame = Frame(card, bg="white")
        text_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        Label(text_frame, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#64748B").pack(anchor="w")
        Label(text_frame, text=val, font=("Segoe UI", 20, "bold"), bg="white", fg=color).pack(anchor="w", pady=(5,0))

        # Icon (Right Side)
        try:
            img = Image.open(resource_path(f"asserts/icons/{icon_filename}")).resize((45, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.dash_icons.append(photo) # Crucial: prevents the image from disappearing!
            
            Label(card, image=photo, bg="white").pack(side=RIGHT, padx=15)
        except Exception as e:
            print(f"DEBUG: Could not load {icon_filename} in dashboard: {e}")

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
            # Printing to terminal so we can see if there is a column mismatch in the sales table
            print(f"DEBUG Dashboard Table Error: {e}")

    def stop_tasks(self):
        self.running = False