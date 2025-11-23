import customtkinter as ctk
from tkinter import messagebox
import database
from auth_ui import AuthApp
from dashboard_ui import DashboardFrame
from add_patient_ui import AddPatientForm
from treatment_ui import TreatmentPage

# Configuration
ctk.set_appearance_mode("Light") # Force Light mode for the Web-style look
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTkFrame):
    def __init__(self, parent, doctor_name):
        super().__init__(parent)
        self.parent = parent
        self.doctor_name = doctor_name
        self.pack(fill="both", expand=True)

        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # ============================================================
        # 1. LEFT SIDEBAR (Dark Modern Style)
        # ============================================================
        # Dark Charcoal color for professional contrast
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#212529")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # -- A. BRANDING HEADER --
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=50)
        self.logo_frame.pack(pady=(20, 10), fill="x")
        
        lbl_logo_icon = ctk.CTkLabel(self.logo_frame, text="✚", font=("Arial", 30), text_color="#2cc985")
        lbl_logo_icon.pack(side="left", padx=(20, 5))
        
        lbl_logo_text = ctk.CTkLabel(self.logo_frame, text="MEDICARE\nCLINIC", font=("Arial", 16, "bold"), text_color="white", justify="left")
        lbl_logo_text.pack(side="left")

        # -- B. DOCTOR PROFILE CARD --
        self.user_card = ctk.CTkFrame(self.sidebar, fg_color="#343a40", corner_radius=10)
        self.user_card.pack(fill="x", padx=15, pady=20)
        
        # User Icon (Unicode)
        lbl_user_icon = ctk.CTkLabel(self.user_card, text="👤", font=("Arial", 26), text_color="white")
        lbl_user_icon.pack(side="left", padx=10, pady=10)
        
        # Doctor Name
        user_info_frame = ctk.CTkFrame(self.user_card, fg_color="transparent")
        user_info_frame.pack(side="left")
        
        lbl_welcome = ctk.CTkLabel(user_info_frame, text="Welcome,", font=("Arial", 10), text_color="gray80")
        lbl_welcome.pack(anchor="w")
        
        lbl_doc_name = ctk.CTkLabel(user_info_frame, text=f"Dr. {doctor_name}", font=("Arial", 12, "bold"), text_color="white")
        lbl_doc_name.pack(anchor="w")

        # -- C. NAVIGATION BUTTONS --
        # Helper function to make buttons look alike
        def create_nav_btn(text, command):
            return ctk.CTkButton(self.sidebar, 
                                 text=text, 
                                 fg_color="transparent", 
                                 text_color="#adb5bd", 
                                 hover_color="#495057", 
                                 anchor="w", 
                                 height=45,
                                 font=("Arial", 14),
                                 command=command)

        # Dashboard Button
        self.btn_dash = create_nav_btn("  🏠   Dashboard", self.show_dashboard)
        self.btn_dash.pack(fill="x", pady=2)
        
        # Add Patient Button
        self.btn_add_pat = create_nav_btn("  ➕   Add Patient", self.show_add_patient)
        self.btn_add_pat.pack(fill="x", pady=2)
        
        # Add Treatment
        self.btn_treat = create_nav_btn("  💊   Treatment", self.show_treatment_page)
        self.btn_treat.pack(fill="x", pady=2)

        # Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#495057").pack(fill="x", pady=20, padx=15)

        # Logout Button (Red Accent)
        self.btn_logout = ctk.CTkButton(self.sidebar, 
                                        text="  ⬅   Logout", 
                                        fg_color="#dc3545", 
                                        hover_color="#c82333", 
                                        anchor="w",
                                        height=40,
                                        command=self.logout)
        self.btn_logout.pack(side="bottom", pady=30, padx=20, fill="x")

        # --- Right Content Area ---
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="#F4F6F9") # Light Grey Background
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        self.view_dashboard = None
        self.view_add_patient = None
        
        # Start
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def set_active_button(self, btn_name):
        """Highlights the active menu item"""
        # Reset colors
        default_color = "transparent"
        active_color = "#02c39a" # Medical Green Highlight
        text_default = "#adb5bd"
        text_active = "white"

        self.btn_dash.configure(fg_color=default_color, text_color=text_default)
        self.btn_add_pat.configure(fg_color=default_color, text_color=text_default)
        self.btn_treat.configure(fg_color=default_color, text_color=text_default)
        
        # Set Active
        if btn_name == "dashboard":
            self.btn_dash.configure(fg_color=active_color, text_color=text_active)
        elif btn_name == "add_patient":
            self.btn_add_pat.configure(fg_color=active_color, text_color=text_active)
        elif btn_name == "treatment":
            self.btn_treat.configure(fg_color=active_color, text_color=text_active)

    def show_dashboard(self):
        self.clear_content()
        self.set_active_button("dashboard")
        self.view_dashboard = DashboardFrame(self.content_area, self.open_patient_details)
        self.view_dashboard.pack(fill="both", expand=True)

    def show_add_patient(self):
        self.clear_content()
        self.set_active_button("add_patient")
        self.view_add_patient = AddPatientForm(self.content_area, self.doctor_name)
        self.view_add_patient.pack(fill="both", expand=True)
        
    def show_treatment_page(self, reg_number=None):
        from treatment_ui import TreatmentPage # Lazy import
        
        self.clear_content()
        self.set_active_button("treatment")
        
        self.view_treatment = TreatmentPage(self.content_area, reg_number)
        self.view_treatment.pack(fill="both", expand=True)

    def open_patient_details(self, reg_number):
        # Update the Dashboard callback to go to Treatment Page
        self.show_treatment_page(reg_number)    

    def open_patient_details(self, reg_number):
        self.show_treatment_page(reg_number)

    def logout(self):
        self.parent.logout()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Management System")
        self.geometry("1200x750")
        
        database.init_db()
        database.create_patient_table()
        database.create_treatment_tables()
        
        # self.show_login()
        self.login_success("Dr. Aftab Ahmed")
    
    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.auth_screen = AuthApp(self, self.login_success)

    def login_success(self, doctor_name):
        if hasattr(self, 'auth_screen'):
            self.auth_screen.destroy()
        self.main_app = MainApplication(self, doctor_name)
        
    def logout(self):
        if hasattr(self, 'main_app'):
            self.main_app.destroy()
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()