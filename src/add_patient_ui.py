import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime

class AddPatientForm(ctk.CTkFrame):
    def __init__(self, parent, doctor_name):
        # 1. OUTER FRAME: Set to WHITE
        super().__init__(parent, fg_color="white") 
        self.doctor_name = doctor_name
        
        # --- Header ---
        self.lbl_title = ctk.CTkLabel(self, text="New Patient Registration", 
                                      font=("Arial", 24, "bold"), text_color="#333")
        self.lbl_title.pack(pady=20)

        # --- Scrollable Container (Inner Frame) ---
        # 2. INNER FRAME: Set to Dashboard Grey (#F4F6F9)
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=700, height=500, 
                                                   fg_color="#F4F6F9", # Dashboard Color
                                                   corner_radius=10)   # Rounded corners
        self.scroll_frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # Configure Grid
        self.scroll_frame.grid_columnconfigure(0, weight=1) 
        self.scroll_frame.grid_columnconfigure(1, weight=3) 

        # 3. INPUT STYLING: Inputs should be White to stand out on Grey
        self.input_bg = "white"
        self.text_col = "black"
        self.border_col = "#d6d6d6"

        # --- Form Fields Construction ---
        
        # 1. Registration Number
        self.create_label(0, "Registration Number:")
        self.entry_reg = self.create_entry()
        self.entry_reg.grid(row=0, column=1, sticky="ew", padx=20, pady=10)
        self.generate_reg_number()

        # 2. Registration Date
        self.create_label(1, "Registration Date:")
        self.entry_date = self.create_entry()
        self.entry_date.grid(row=1, column=1, sticky="ew", padx=20, pady=10)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 3. Patient Name
        self.create_label(2, "Patient Name:")
        name_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        name_frame.grid(row=2, column=1, sticky="ew", padx=20, pady=10)
        
        self.combo_title = ctk.CTkComboBox(name_frame, values=["Mr.", "Ms.", "Mrs.", "Mts.", "Dr."], width=70, height=35, 
                                           fg_color=self.input_bg, text_color=self.text_col, border_color=self.border_col)
        self.combo_title.pack(side="left", padx=(0, 10))
        
        self.entry_name = self.create_entry(master=name_frame, placeholder="Full Name")
        self.entry_name.pack(side="left", fill="x", expand=True)

        # 4. Gender & Age
        self.create_label(3, "Gender & Age:")
        ga_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        ga_frame.grid(row=3, column=1, sticky="ew", padx=20, pady=10)
        
        self.combo_gender = ctk.CTkComboBox(ga_frame, values=["Male", "Female", "Other"], width=120, height=35, 
                                            fg_color=self.input_bg, text_color=self.text_col, border_color=self.border_col)
        self.combo_gender.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(ga_frame, text="Age:", text_color="#333").pack(side="left", padx=(10, 5))
        self.entry_age = self.create_entry(master=ga_frame, placeholder="Ex: 32", width=80)
        self.entry_age.pack(side="left")

        # 5. Contact Number
        self.create_label(4, "Contact Number:")
        self.entry_contact = self.create_entry()
        self.entry_contact.grid(row=4, column=1, sticky="ew", padx=20, pady=10)

        # 6. Address
        self.create_label(5, "Address:")
        self.txt_address = ctk.CTkTextbox(self.scroll_frame, height=80, fg_color=self.input_bg, 
                                          text_color=self.text_col, border_color=self.border_col, border_width=2)
        self.txt_address.grid(row=5, column=1, sticky="ew", padx=20, pady=10)
        
        # 7. Patient Type
        self.create_label(6, "Patient Type:")
        self.combo_type = ctk.CTkComboBox(self.scroll_frame, values=["New", "Old/Follow-up"], height=35, 
                                          fg_color=self.input_bg, text_color=self.text_col, border_color=self.border_col)
        self.combo_type.grid(row=6, column=1, sticky="ew", padx=20, pady=10)

        # 8. Consultant
        self.create_label(7, "Consulting Doctor:")
        self.entry_doc = self.create_entry()
        self.entry_doc.grid(row=7, column=1, sticky="ew", padx=20, pady=10)
        self.entry_doc.insert(0, self.doctor_name)
        self.entry_doc.configure(state="disabled")

        # --- Save Button ---
        self.btn_save = ctk.CTkButton(self.scroll_frame, text="Save Patient Record", 
                                      fg_color="#28a745", hover_color="#218838", # Bootstrap Green
                                      height=45, 
                                      font=("Arial", 14, "bold"),
                                      command=self.save_patient)
        self.btn_save.grid(row=8, column=1, sticky="w", padx=20, pady=40)

    def create_label(self, row_idx, text):
        """Helper to create consistent labels with dark text"""
        lbl = ctk.CTkLabel(self.scroll_frame, text=text, font=("Arial", 14), text_color="#555")
        lbl.grid(row=row_idx, column=0, sticky="ne", padx=20, pady=15)

    def create_entry(self, master=None, placeholder="", width=None):
        """Helper to create consistent white input fields"""
        if master is None:
            master = self.scroll_frame
            
        entry = ctk.CTkEntry(master, height=35, 
                             fg_color=self.input_bg, 
                             text_color=self.text_col, 
                             border_color=self.border_col,
                             placeholder_text=placeholder)
        if width:
            entry.configure(width=width)
        return entry

    def generate_reg_number(self):
        next_id = database.get_next_patient_id()
        year = datetime.now().year
        reg_str = f"REG-{year}-{next_id:04d}"
        self.entry_reg.delete(0, "end")
        self.entry_reg.insert(0, reg_str)

    def save_patient(self):
        reg_num = self.entry_reg.get()
        reg_date = self.entry_date.get()
        
        title = self.combo_title.get()
        raw_name = self.entry_name.get()
        full_name = f"{title} {raw_name}" if raw_name else ""
        
        gender = self.combo_gender.get()
        age = self.entry_age.get()
        contact = self.entry_contact.get()
        address = self.txt_address.get("1.0", "end-1c")
        p_type = self.combo_type.get()
        consultant = self.doctor_name

        if not raw_name or not contact or not age:
            messagebox.showwarning("Missing Data", "Name, Age, and Contact are required.")
            return

        success, message = database.add_patient(
            reg_num, reg_date, full_name, gender, age, address, contact, p_type, consultant
        )

        if success:
            messagebox.showinfo("Success", "Patient Registered Successfully!")
            self.clear_form()
            self.generate_reg_number()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_age.delete(0, "end")
        self.entry_contact.delete(0, "end")
        self.txt_address.delete("1.0", "end")