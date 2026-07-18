from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from connection import connect, resource_path
import os

from modules.dashboard import Dashboard
from modules.menu import Menu
from modules.orders import Orders
from modules.billing import Billing
from modules.reports import Reports

class Main:
    def __init__(self):
        self.root = Tk()
        self.root.title("Canteen Ordering System")
        self.root.state("zoomed")
        
        # Colors 
        self.sidebar_bg = "#064E3B"
        self.sidebar_active = "#047857" # Lighter green for hover effects!
        self.header_bg = "#FFFFFF"
        self.content_bg = "#F8FAFC"
        
        # To store images and track the buttons for highlighting
        self.icon_refs = [] 
        self.sidebar_btns = {}
        self.current_active_tab = "" # Tracks which tab is currently white
        
        self.build_login()
        self.root.mainloop()

    def build_login(self):
        self.login_frame = Frame(self.root, bg=self.sidebar_active)
        self.login_frame.pack(fill=BOTH, expand=True)
        
        card = Frame(self.login_frame, bg="white", padx=60, pady=45, bd=0)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        try:
            logo_img = Image.open(resource_path("asserts/logos/canteen_logo.png")).resize((85, 85), Image.Resampling.LANCZOS)
            self.login_logo = ImageTk.PhotoImage(logo_img)
            Label(card, image=self.login_logo, bg="white").pack(pady=(0, 10))
        except Exception as e:
            print(f"DEBUG: Could not load login logo: {e}")
            
        Label(card, text="Canteen Admin", font=("Segoe UI", 24, "bold"), bg="white", fg="#0F172A").pack()
        Label(card, text="Sign in to continue to your dashboard", font=("Segoe UI", 11), bg="white", fg="#64748B").pack(pady=(0, 30))
        
        Label(card, text="USERNAME", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack(anchor="w")
        self.u_entry = Entry(card, font=("Segoe UI", 13), width=32, bg="#F1F5F9", fg="#0F172A", relief=FLAT)
        self.u_entry.pack(pady=(5, 15), ipady=8)
        
        p_lbl_frame = Frame(card, bg="white")
        p_lbl_frame.pack(fill=X)
        
        Label(p_lbl_frame, text="PASSWORD", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").pack(side=LEFT)
        
        self.toggle_btn = Label(p_lbl_frame, text="👁 Show", font=("Segoe UI", 9, "bold"), bg="white", fg="#3B82F6", cursor="hand2")
        self.toggle_btn.pack(side=RIGHT)
        self.toggle_btn.bind("<Button-1>", self.toggle_password) 
        
        self.p_entry = Entry(card, font=("Segoe UI", 13), width=32, show="*", bg="#F1F5F9", fg="#0F172A", relief=FLAT)
        self.p_entry.pack(pady=(5, 25), ipady=8)
        
        Button(card, text="LOGIN", bg="#10B981", fg="white", font=("Segoe UI", 12, "bold"), 
               command=self.check_login, cursor="hand2", bd=0, activebackground="#059669", activeforeground="white").pack(fill=X, ipady=8)

    def toggle_password(self, event=None):
        if self.p_entry.cget("show") == "*":
            self.p_entry.config(show="")  
            self.toggle_btn.config(text="🙈 Hide", fg="#64748B") 
        else:
            self.p_entry.config(show="*") 
            self.toggle_btn.config(text="👁 Show", fg="#3B82F6") 

    def check_login(self):
        u, p = self.u_entry.get(), self.p_entry.get()
        try:
            conn = connect()
            cr = conn.cursor()
            cr.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (u, p))
            if cr.fetchone():
                self.login_frame.destroy()
                self.setup_ui(u)
            else:
                messagebox.showerror("Error", "Invalid Credentials")
            conn.close()
        except Exception as e: messagebox.showerror("Error", str(e))

    def setup_ui(self, username):
        header = Frame(self.root, bg=self.header_bg, height=70)
        header.pack(fill=X)
        Label(header, text="CANTEEN SYSTEM", font=("Segoe UI", 20, "bold"), bg=self.header_bg, fg="#064E3B").pack(side=LEFT, padx=30)
        Button(header, text="Logout", bg="#FEE2E2", fg="#EF4444", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.exit_app, padx=15, pady=5).pack(side=RIGHT, padx=30)
        
        self.main_cont = Frame(self.root, bg=self.content_bg)
        self.main_cont.pack(fill=BOTH, expand=True)
        
        self.sidebar = Frame(self.main_cont, bg=self.sidebar_bg, width=240)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)
        
        self.content_area = Frame(self.main_cont, bg=self.content_bg)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)

        try:
            logo_img = Image.open(resource_path("asserts/logos/canteen_logo.png")).resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            Label(self.sidebar, image=self.logo_photo, bg=self.sidebar_bg).pack(pady=(20, 20))
        except Exception as e:
            Label(self.sidebar, text="[LOGO HERE]", font=("Segoe UI", 12, "bold"), bg=self.sidebar_bg, fg="white").pack(pady=(20, 20))

        Label(self.sidebar, text="MAIN MENU", font=("Segoe UI", 10, "bold"), bg=self.sidebar_bg, fg="#A7F3D0", anchor="w").pack(fill=X, padx=20, pady=(0, 10))

        btns = [
            ("Dashboard", "dashboard.png", self.show_dashboard), 
            ("Food Menu", "menu.png", self.show_menu), 
            ("Orders", "orders.png", self.show_orders), 
            ("Billing", "billing.png", self.show_billing), 
            ("Reports", "reports.png", self.show_reports),
            ("Exit", "exit.png", self.exit_app)
        ]
        
        for name, icon_file, cmd in btns:
            try:
                img = Image.open(resource_path(f"asserts/logos/{icon_file}")).resize((24, 24), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.icon_refs.append(photo) 
                
                def command_wrapper(n=name, c=cmd):
                    self.update_highlight(n)
                    c()

                btn = Button(self.sidebar, text=f"   {name}", image=photo, compound=LEFT, bd=0, 
                             font=("Segoe UI", 12, "bold"), anchor="w", padx=20, pady=12, cursor="hand2", 
                             activebackground="white", activeforeground=self.sidebar_bg, command=command_wrapper)
                btn.pack(fill=X)
                self.sidebar_btns[name] = btn  
                
            except Exception as e:
                def command_wrapper_fallback(n=name, c=cmd):
                    self.update_highlight(n)
                    c()
                btn = Button(self.sidebar, text=name, bd=0, font=("Segoe UI", 12, "bold"), 
                             anchor="w", padx=20, pady=12, cursor="hand2", 
                             activebackground="white", activeforeground=self.sidebar_bg, command=command_wrapper_fallback)
                btn.pack(fill=X)
                self.sidebar_btns[name] = btn  

            # --- NEW: Bind Hover Animations ---
            btn.bind("<Enter>", lambda event, n=name: self.on_hover_enter(n))
            btn.bind("<Leave>", lambda event, n=name: self.on_hover_leave(n))
        
        Label(self.sidebar, text=f"● {username} (Online)", bg=self.sidebar_bg, fg="white", font=("Segoe UI", 10)).pack(side=BOTTOM, pady=20, anchor="w", padx=20)
        
        self.update_highlight("Dashboard")
        self.show_dashboard()

    # --- NEW HOVER ANIMATION LOGIC ---
    def on_hover_enter(self, name):
        """Highlights the button slightly when hovered, unless it's the active tab."""
        if self.current_active_tab != name:
            self.sidebar_btns[name].config(bg=self.sidebar_active)

    def on_hover_leave(self, name):
        """Reverts the button color when mouse leaves, unless it's the active tab."""
        if self.current_active_tab != name:
            self.sidebar_btns[name].config(bg=self.sidebar_bg)
    # ---------------------------------

    def update_highlight(self, active_name):
        self.current_active_tab = active_name # Update the tracker
        for name, btn in self.sidebar_btns.items():
            if name == active_name:
                btn.config(bg="white", fg=self.sidebar_bg) 
            else:
                btn.config(bg=self.sidebar_bg, fg="white") 

    def clear_content(self):
        for w in self.content_area.winfo_children():
            if hasattr(w, 'stop_tasks'): w.stop_tasks()
            w.destroy()

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to close the Canteen System?"):
            self.root.destroy()

    def show_dashboard(self): self.clear_content(); Dashboard(self.content_area)
    def show_menu(self): self.clear_content(); Menu(self.content_area)
    def show_orders(self): self.clear_content(); Orders(self.content_area)
    def show_billing(self): self.clear_content(); Billing(self.content_area)
    def show_reports(self): self.clear_content(); Reports(self.content_area)

if __name__ == "__main__": Main()