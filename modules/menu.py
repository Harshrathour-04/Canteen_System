from tkinter import *
from tkinter import ttk, messagebox
from connection import connect

class Menu:
    def __init__(self, parent):
        self.running = True  
        self.frame = Frame(parent, bg="#F8FAFC")
        self.frame.pack(fill=BOTH, expand=True)

        self.item_name = StringVar()
        self.category = StringVar()
        self.price = StringVar()
        self.available = StringVar()
        self.current_id = None

        # Header
        Label(self.frame, text="Food Menu Management", font=("Segoe UI", 24, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 20))

        # Content split container
        content = Frame(self.frame, bg="#F8FAFC")
        content.pack(fill=BOTH, expand=True)

        # --- Left Side: Input Form ---
        form_card = Frame(content, bg="white", width=350, highlightbackground="#E2E8F0", highlightthickness=1)
        form_card.pack(side=LEFT, fill=Y, padx=(0, 20))
        form_card.pack_propagate(False)

        Label(form_card, text="Item Details", font=("Segoe UI", 16, "bold"), bg="white", fg="#0F172A").pack(pady=20)

        self.make_input(form_card, "Food Name", self.item_name)
        
        Label(form_card, text="Category", font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").pack(anchor="w", padx=20)
        cat_box = ttk.Combobox(form_card, textvariable=self.category, values=("Beverages", "Fast Food", "Desserts", "Meals"), state="readonly", font=("Segoe UI", 11))
        cat_box.pack(fill=X, padx=20, pady=(5, 15))
        
        self.make_input(form_card, "Price (₹)", self.price)
        
        Label(form_card, text="Available", font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").pack(anchor="w", padx=20)
        avail_box = ttk.Combobox(form_card, textvariable=self.available, values=("Yes", "No"), state="readonly", font=("Segoe UI", 11))
        avail_box.pack(fill=X, padx=20, pady=(5, 20))

        # Action Buttons
        btn_frm = Frame(form_card, bg="white")
        btn_frm.pack(fill=X, padx=20)
        Button(btn_frm, text="Add", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.add_item).pack(side=LEFT, expand=True, fill=X, padx=2, ipady=4)
        Button(btn_frm, text="Update", bg="#3B82F6", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.update_item).pack(side=LEFT, expand=True, fill=X, padx=2, ipady=4)
        
        btn_frm2 = Frame(form_card, bg="white")
        btn_frm2.pack(fill=X, padx=20, pady=5)
        Button(btn_frm2, text="Delete", bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.delete_item).pack(side=LEFT, expand=True, fill=X, padx=2, ipady=4)
        Button(btn_frm2, text="Clear", bg="#64748B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.clear_data).pack(side=LEFT, expand=True, fill=X, padx=2, ipady=4)

        # --- Right Side: Data Table ---
        table_card = Frame(content, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        table_card.pack(side=LEFT, fill=BOTH, expand=True)

        # Style the Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#FFFFFF", foreground="#64748B")

        self.table = ttk.Treeview(table_card, columns=("ID", "Name", "Category", "Price", "Available"), show="headings")
        for col in ("ID", "Name", "Category", "Price", "Available"):
            self.table.heading(col, text=col.upper())
            self.table.column(col, anchor=CENTER, width=100 if col != "Name" else 200)
            
        self.table.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.table.bind("<ButtonRelease-1>", self.get_cursor)

        self.fetch_data()

    def stop_tasks(self):
        self.running = False 

    def make_input(self, parent, label, var):
        Label(parent, text=label, font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").pack(anchor="w", padx=20)
        Entry(parent, textvariable=var, font=("Segoe UI", 11), bg="#F8FAFC", relief=SOLID, bd=1).pack(fill=X, padx=20, pady=(5, 15), ipady=4)

    def fetch_data(self):
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("SELECT * FROM menu")
            rows = cr.fetchall()
            if self.running:
                self.table.delete(*self.table.get_children())
                for row in rows: 
                    self.table.insert('', END, values=row)
            conn.close()
        except: pass

    def clear_data(self):
        self.item_name.set("")
        self.category.set("")
        self.price.set("")
        self.available.set("")
        self.current_id = None

    def get_cursor(self, ev):
        cursor_row = self.table.focus()
        if not cursor_row: return
        row = self.table.item(cursor_row)['values']
        if row:
            self.current_id = row[0]
            self.item_name.set(row[1])
            self.category.set(row[2])
            self.price.set(row[3])
            self.available.set(row[4])

    def add_item(self):
        name, cat, prc, avail = self.item_name.get(), self.category.get(), self.price.get(), self.available.get()
        if not name or not prc: 
            return messagebox.showerror("Error", "Name and Price required")
            
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("INSERT INTO menu (item_name, category, price, available) VALUES (%s, %s, %s, %s)", (name, cat, prc, avail))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_data()
            messagebox.showinfo("Success", "Item Added Successfully")
        except Exception as e: 
            if self.running: messagebox.showerror("Database Error", str(e))

    def update_item(self):
        if not self.current_id: 
            return messagebox.showerror("Error", "Please select an item to update")
            
        name, cat, prc, avail = self.item_name.get(), self.category.get(), self.price.get(), self.available.get()
        try:
            conn = connect()
            cr = conn.cursor()
            # Changed 'id' to 'item_id' in the query below
            cr.execute("UPDATE menu SET item_name=%s, category=%s, price=%s, available=%s WHERE item_id=%s", (name, cat, prc, avail, self.current_id))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_data()
            messagebox.showinfo("Success", "Item Updated Successfully")
        except Exception as e: 
            if self.running: messagebox.showerror("Database Error", str(e))

    def delete_item(self):
        if not self.current_id: 
            return messagebox.showerror("Error", "Please select an item to delete")
            
        try:
            conn = connect()
            cr = conn.cursor()
            # Changed 'id' to 'item_id' in the query below
            cr.execute("DELETE FROM menu WHERE item_id=%s", (self.current_id,))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_data()
            messagebox.showinfo("Success", "Item Deleted Successfully")
        except Exception as e: 
            if self.running: messagebox.showerror("Database Error", str(e))