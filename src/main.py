import customtkinter as ctk
from tkinter import messagebox
import database
from auth_ui import AuthApp
from dashboard_ui import DashboardFrame
from add_patient_ui import AddPatientForm

# Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTkFrame):
    def __init__(self, parent, doctor_name):
        super().__init__(parent)
        self.parent = parent
        self.doctor_name = doctor_name
        self.pack(fill="both", expand=True)

        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1) # Content area expands
        self.grid_rowconfigure(0, weight=1)

        # --- Left Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#02c39a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Doctor's App", font=("Arial", 20, "bold"))
        self.logo_label.pack(pady=30)
        
        # Navigation Buttons
        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.show_dashboard)
        self.btn_dash.pack(pady=10, padx=20, fill="x")
        
        self.btn_add_pat = ctk.CTkButton(self.sidebar, text="Add Patient", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.show_add_patient)
        self.btn_add_pat.pack(pady=10, padx=20, fill="x")

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", fg_color="#a62e2e", hover_color="#701515", command=self.logout)
        self.btn_logout.pack(side="bottom", pady=20, padx=20, fill="x")

        # --- Right Content Area ---
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Initialize Views
        self.view_dashboard = None
        self.view_add_patient = None
        
        # Start with Dashboard
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        # Highlight button
        self.btn_dash.configure(fg_color=("gray75", "gray25"))
        self.btn_add_pat.configure(fg_color="transparent")
        
        # Load Dashboard
        self.view_dashboard = DashboardFrame(self.content_area, self.open_patient_details)
        self.view_dashboard.pack(fill="both", expand=True)

    def show_add_patient(self):
        self.clear_content()
        self.btn_dash.configure(fg_color="transparent")
        self.btn_add_pat.configure(fg_color=("gray75", "gray25"))
        
        label = ctk.CTkLabel(self.content_area, text="Add Patient Form (Coming Next Step)", font=("Arial", 24))
        label.pack(pady=50)
        
        # Temporary button to test Data adding
        btn_test = ctk.CTkButton(self.content_area, text="Add Dummy Patient for Testing", command=self.add_dummy_data)
        btn_test.pack()
        
    def add_dummy_data(self):
        import random
        # Helper to test dashboard
        num = random.randint(1000, 9999)
        database.add_patient(
            f"REG-{num}", "2024-05-20", f"Test Patient {num}", 
            "Male", "30", "123 Secret St", "555-0192", "New", self.doctor_name
        )
        messagebox.showinfo("Info", "Dummy patient added. Go to Dashboard to view.")

    def open_patient_details(self, reg_number):
        # This will handle opening the specific patient view (Requirement D)
        print(f"Opening details for: {reg_number}")
        messagebox.showinfo("Action", f"Opening details for {reg_number} \n(Layout coming in next step)")
        
    def show_add_patient(self):
        self.clear_content()

        # Toggle button styles
        self.btn_dash.configure(fg_color="transparent")
        self.btn_add_pat.configure(fg_color=("gray75", "gray25"))

        # Load the real form
        self.view_add_patient = AddPatientForm(self.content_area, self.doctor_name)
        self.view_add_patient.pack(fill="both", expand=True)

    def logout(self):
        self.parent.logout()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Management System")
        self.geometry("1100x700")
        
        database.init_db()
        database.create_patient_table() # Ensure patient table exists
        
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.auth_screen = AuthApp(self, self.login_success)

    def login_success(self, doctor_name):
        self.auth_screen.destroy()
        self.main_app = MainApplication(self, doctor_name)
        
    def logout(self):
        if hasattr(self, 'main_app'):
            self.main_app.destroy()
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()