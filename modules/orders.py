from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from connection import connect

class Orders:
    def __init__(self, parent):
        self.running = True  # Safety flag
        self.frame = Frame(parent, bg="#F8FAFC")
        self.frame.pack(fill=BOTH, expand=True)

        self.item_name = StringVar()
        self.quantity = StringVar()
        self.price = StringVar()

        # Header
        Label(self.frame, text="Take New Order", font=("Segoe UI", 24, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 20))

        # --- Top Section: Input Form ---
        form_card = Frame(self.frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        form_card.pack(fill=X, pady=(0, 20))
        
        input_frame = Frame(form_card, bg="white")
        input_frame.pack(pady=20, padx=20, fill=X)

        Label(input_frame, text="Select Item", font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").grid(row=0, column=0, padx=10, sticky="w")
        self.item_box = ttk.Combobox(input_frame, textvariable=self.item_name, width=25, font=("Segoe UI", 11), state="readonly")
        self.item_box.grid(row=1, column=0, padx=10, pady=(5, 10))
        self.item_box.bind("<<ComboboxSelected>>", self.get_price)

        Label(input_frame, text="Quantity", font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").grid(row=0, column=1, padx=10, sticky="w")
        Entry(input_frame, textvariable=self.quantity, width=15, font=("Segoe UI", 11), bg="#F8FAFC", relief=SOLID, bd=1).grid(row=1, column=1, padx=10, pady=(5, 10), ipady=4)

        Label(input_frame, text="Unit Price (₹)", font=("Segoe UI", 10, "bold"), bg="white", fg="#64748B").grid(row=0, column=2, padx=10, sticky="w")
        Entry(input_frame, textvariable=self.price, width=15, state="readonly", font=("Segoe UI", 11), bg="#F1F5F9", relief=SOLID, bd=1).grid(row=1, column=2, padx=10, pady=(5, 10), ipady=4)

        Button(input_frame, text="➕ Add to Cart", font=("Segoe UI", 11, "bold"), bg="#3B82F6", fg="white", cursor="hand2", bd=0, padx=20, command=self.add_to_cart).grid(row=1, column=3, padx=20, ipady=2)

        # --- Bottom Section: Cart Table ---
        Label(self.frame, text="Current Cart", font=("Segoe UI", 14, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 10))
        
        table_card = Frame(self.frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        table_card.pack(fill=BOTH, expand=True)

        self.cart_table = ttk.Treeview(table_card, columns=("Item", "Qty", "Price", "Total"), show="headings")
        for col in ("Item", "Qty", "Price", "Total"):
            self.cart_table.heading(col, text=col.upper())
            self.cart_table.column(col, anchor=CENTER)
        self.cart_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Action Button
        Button(self.frame, text="📝 Place Order", font=("Segoe UI", 14, "bold"), bg="#10B981", fg="white", cursor="hand2", bd=0, pady=12, command=self.place_order).pack(fill=X, pady=(20, 0))

        self.load_items()

    def stop_tasks(self):
        self.running = False

    def load_items(self):
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("SELECT item_name FROM menu WHERE available='Yes'")
            data = cr.fetchall()
            if self.running: 
                self.item_box["values"] = [row[0] for row in data]
            conn.close()
        except: pass

    def get_price(self, event):
        item = self.item_name.get()
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("SELECT price FROM menu WHERE item_name=%s", (item,))
            data = cr.fetchone()
            if self.running and data: 
                self.price.set(data[0])
            conn.close()
        except: pass

    def add_to_cart(self):
        name, qty_str, prc_str = self.item_name.get(), self.quantity.get(), self.price.get()
        if not name or not qty_str:
            return messagebox.showerror("Error", "Select an item and enter quantity")
        try:
            qty, price = int(qty_str), float(prc_str)
            self.cart_table.insert("", END, values=(name, qty, price, qty * price))
            self.item_name.set(""); self.quantity.set(""); self.price.set("")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")

    def place_order(self):
        records = self.cart_table.get_children()
        if not records: 
            return messagebox.showerror("Error", "Cart is empty!")
            
        customer = simpledialog.askstring("Customer Name", "Enter customer name:")
        if not customer: return

        items_list = []
        grand_total = 0.0
        
        for row in records:
            data = self.cart_table.item(row)["values"]
            items_list.append(f"{data[0]} (x{data[1]})")
            grand_total += float(data[3])
            
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("INSERT INTO sales (customer_name, items_ordered, total_items, grand_total, status) VALUES (%s, %s, %s, %s, %s)", 
                       (customer, ", ".join(items_list), len(records), grand_total, 'Pending'))
            conn.commit() 
            conn.close()
            
            if self.running:
                messagebox.showinfo("Success", "Order Placed Successfully!")
                for row in records: self.cart_table.delete(row)
        except Exception as e: 
            if self.running: messagebox.showerror("Database Error", str(e))