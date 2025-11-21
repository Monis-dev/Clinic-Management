import customtkinter as ctk
from tkinter import messagebox
import database

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

ADMIN_REGISTRATION_KEY = "DOC_2025-KEY"

class AuthApp(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.show_login()

    def clear_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
            
    def show_login(self):
        self.clear_frame()
        
        label = ctk.CTkLabel(self.center_frame, text="Login", font=("Arial", 24, "bold"))
        label.pack(pady=20, padx=40)
        
        self.entry_user = ctk.CTkEntry(self.center_frame, placeholder_text="Username")
        self.entry_user.pack(pady=10, padx=20)
        
        self.entry_pass = ctk.CTkEntry(self.center_frame, placeholder_text="Password")
        self.entry_pass.pack(pady=10, padx=20)
        
        btn_login = ctk.CTkButton(self.center_frame, text="Login", command=self.perform_login)
        btn_login.pack(pady=20)
        
        btn_reg_link = ctk.CTkButton(self.center_frame, text="Create New account",
                        fg_color="transparent", hover_color="#444", command=self.show_register)
        btn_reg_link.pack(pady=5)
        
    def show_register(self):
        self.clear_frame()
        
        label = ctk.CTkLabel(self.center_frame, text="Registration", font=("Arial", 24, "bold"))   
        label.pack(pady=20, padx=40)
        
        self.reg_fullname = ctk.CTkEntry(self.center_frame, placeholder_text="Enter full name")
        self.reg_fullname.pack(pady=5, padx=20)
        
        self.reg_user = ctk.CTkEntry(self.center_frame, placeholder_text="Enter user name")
        self.reg_user.pack(pady=5, padx=20)
        
        self.reg_pass = ctk.CTkEntry(self.center_frame, placeholder_text="Password", show="*")
        self.reg_pass.pack(pady=5, padx=20)
        
        self.reg_key = ctk.CTkEntry(self.center_frame, placeholder_text="Registration Key")
        self.reg_key.pack(pady=5, padx=20)
        
        btn_register = ctk.CTkButton(self.center_frame, text="Register", command=self.perform_register)
        btn_register.pack(pady=20)
        
        btn_back = ctk.CTkButton(self.center_frame, text="Back to Login", fg_color="transparent", hover_color="#444", command=self.show_login)
        btn_back.pack(pady=5)
        
    def perform_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        success, message = database.login_doctor(user, pwd)

        if success:
            self.on_login_success(message)
        else:
            messagebox.showerror("Login Failed", message)

    def perform_register(self):
        name = self.reg_fullname.get()
        user = self.reg_user.get()
        pwd = self.reg_pass.get()
        key = self.reg_key.get()

        if not name or not user or not pwd or not key:
            messagebox.showerror("Error", "All fields are required!")
            return

        if key != ADMIN_REGISTRATION_KEY:
            messagebox.showerror("Error", "Invalid Registratio Key! You cannot register")
            return

        success, msg = database.register_doctor(user, pwd, name)
        if success:
            messagebox.showinfo("Success", "Account created! Please Login!")
            self.show_login()

        else:
            messagebox.showerror("Error", msg)        