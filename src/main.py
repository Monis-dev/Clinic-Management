import customtkinter as ctk
import database
from auth_ui import AuthApp

class MainApplication(ctk.CTkFrame):
    def __init__(self, parent, doctor_name):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        label = ctk.CTkLabel(self, text=f"Welcome, {doctor_name}!", font=("Arial", 30))
        label.place(relx=0.5, rely=0.4, anchor="center")
        
        sub_label = ctk.CTkLabel(self, text="Dashboard Loading...", font=("Arial", 16))
        sub_label.place(relx=0.5, rely=0.5, anchor="center")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Management System")
        self.geometry("900x600")
        database.init_db()
        self.auth_screen = AuthApp(self, self.login_success)
        
    def login_success(self, doctor_name):
        self.auth_screen.destroy()
        
        self.main_app = MainApplication(self, doctor_name)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()                       