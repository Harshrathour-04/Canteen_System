from tkinter import *
from tkinter import messagebox
from connection import connect

class Billing:
    def __init__(self, parent):
        self.running = True  
        self.frame = Frame(parent, bg="#F8FAFC")
        self.frame.pack(fill=BOTH, expand=True)

        self.search_var = StringVar()
        self.loaded_id = None

        # Header
        Label(self.frame, text="Billing & Invoice", font=("Segoe UI", 24, "bold"), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(0, 20))

        # Split screen container
        content = Frame(self.frame, bg="#F8FAFC")
        content.pack(fill=BOTH, expand=True)
        
        # -------------------------------------------------------------
        # LEFT SIDE: Controls (Search, Pay, Print)
        # -------------------------------------------------------------
        left_frame = Frame(content, bg="#F8FAFC", width=350)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # Search Card
        search_card = Frame(left_frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        search_card.pack(fill=X, pady=(0, 20))
        
        sf = Frame(search_card, bg="white")
        sf.pack(pady=20, padx=20, fill=X)
        
        Label(sf, text="Enter Order ID:", font=("Segoe UI", 12, "bold"), bg="white", fg="#0F172A").pack(anchor="w", pady=(0, 5))
        Entry(sf, textvariable=self.search_var, font=("Segoe UI", 14), bg="#F8FAFC", relief=SOLID, bd=1, justify=CENTER).pack(fill=X, ipady=6, pady=(0, 15))
        Button(sf, text="🔍 Fetch Order", bg="#064E3B", fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", pady=10, command=self.fetch_order).pack(fill=X)

        # Actions Card
        action_card = Frame(left_frame, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        action_card.pack(fill=X)
        
        af = Frame(action_card, bg="white")
        af.pack(pady=20, padx=20, fill=X)
        
        Button(af, text="✅ Mark as Paid", bg="#10B981", fg="white", font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2", pady=12, command=self.mark_paid).pack(fill=X, pady=(0, 15))
        Button(af, text="🖨️ Print Invoice", bg="#3B82F6", fg="white", font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2", pady=12, command=self.print_invoice).pack(fill=X)

        # -------------------------------------------------------------
        # RIGHT SIDE: POS Receipt Preview
        # -------------------------------------------------------------
        right_frame = Frame(content, bg="white", highlightbackground="#E2E8F0", highlightthickness=1)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        Label(right_frame, text="Invoice Preview", font=("Segoe UI", 16, "bold"), bg="white", fg="#0F172A").pack(anchor="w", padx=20, pady=20)
        
        # Receipt Box (Using Text widget for a POS printer look)
        receipt_container = Frame(right_frame, bg="#FAFAFA", highlightbackground="#CBD5E1", highlightthickness=1)
        receipt_container.pack(padx=20, pady=(0, 20), fill=BOTH, expand=True)
        
        #font gives it the classic receipt structure
        self.receipt_area = Text(receipt_container, font=("Courier New", 13), bg="#FAFAFA", fg="#0F172A", bd=0, padx=30, pady=30, state=DISABLED)
        self.receipt_area.pack(fill=BOTH, expand=True)
        
        self.clear_receipt()

    def stop_tasks(self):
        self.running = False
        
    def clear_receipt(self):
        self.receipt_area.config(state=NORMAL)
        self.receipt_area.delete("1.0", END)
        self.receipt_area.insert(END, "\n\n\n\n" + "--- NO ORDER LOADED ---".center(45) + "\n" + "Enter an Order ID on the left to view.".center(45))
        self.receipt_area.config(state=DISABLED)
        self.loaded_id = None
        
    def generate_receipt(self, order_id, customer, items, total_items, grand_total, status, date):
        self.receipt_area.config(state=NORMAL)
        self.receipt_area.delete("1.0", END)
        
        # Formatting the POS Receipt
        bill = f"{'='*45}\n"
        bill += f"{'CANTEEN ORDERING SYSTEM'.center(45)}\n"
        bill += f"{'Official Tax Invoice'.center(45)}\n"
        bill += f"{'='*45}\n\n"
        
        bill += f" Order ID  : #{order_id}\n"
        bill += f" Date      : {date}\n"
        bill += f" Customer  : {customer}\n"
        bill += f" Status    : {status.upper()}\n\n"
        
        bill += f"{'-'*45}\n"
        bill += f" ITEMS ORDERED\n"
        bill += f"{'-'*45}\n"
        
        # Split the comma-separated items and list them neatly
        item_list = items.split(", ")
        for item in item_list:
            bill += f"  • {item}\n"
            
        bill += f"{'-'*45}\n"
        bill += f" Total Items: {total_items}\n\n"
        
        # Grand Total Formatting
        bill += f" GRAND TOTAL:                ₹{grand_total:.2f}\n"
        bill += f"{'='*45}\n\n"
        
        if status.lower() == 'paid':
            bill += f"{'*** PAID IN FULL ***'.center(45)}\n"
        else:
            bill += f"{'*** PAYMENT PENDING ***'.center(45)}\n"
            
        bill += f"{'Thank you for your visit!'.center(45)}\n"
        
        self.receipt_area.insert(END, bill)
        self.receipt_area.config(state=DISABLED)
        self.loaded_id = order_id

    def fetch_order(self):
        val = self.search_var.get()
        if not val:
            return messagebox.showerror("Error", "Please enter an Order ID")
            
        try:
            conn = connect()
            cr = conn.cursor()
            # Fetching data including the date
            cr.execute("SELECT customer_name, items_ordered, total_items, grand_total, status, DATE(order_date) FROM sales WHERE order_id = %s", (val,))
            data = cr.fetchone()
            conn.close()
            
            if self.running:
                if data:
                    self.generate_receipt(val, data[0], data[1], data[2], data[3], data[4], data[5])
                else:
                    messagebox.showerror("Not Found", "Order ID not found.")
                    self.clear_receipt()
        except Exception as e:
            if self.running: messagebox.showerror("Database Error", str(e))

    def mark_paid(self):
        if not self.loaded_id:
            return messagebox.showerror("Error", "Please fetch an order first!")
            
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("UPDATE sales SET status='Paid' WHERE order_id=%s", (self.loaded_id,))
            conn.commit()
            conn.close()
            
            if self.running:
                messagebox.showinfo("Success", "Order marked as Paid!")
                # Refresh the receipt automatically to show "PAID"
                self.fetch_order()
        except Exception as e:
            if self.running: messagebox.showerror("Error", str(e))

    def print_invoice(self):
        if not self.loaded_id:
            return messagebox.showerror("Error", "No invoice data to print")
        messagebox.showinfo("Print", "Invoice sent to printer successfully!")