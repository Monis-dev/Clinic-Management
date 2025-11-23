import customtkinter as ctk
from tkinter import messagebox, ttk
import database
from datetime import datetime
from customtkinter.windows.widgets.ctk_scrollable_frame import CTkScrollableFrame

def fixed_check_if_master_is_canvas(self, widget):
    if widget is None:
        return False
    if isinstance(widget, str):
        return False
    
    if widget == self._parent_canvas:
        return True
    elif widget.master is not None:
        return self.check_if_master_is_canvas(widget.master)
    else:
        return False

CTkScrollableFrame.check_if_master_is_canvas = fixed_check_if_master_is_canvas

class TreatmentPage(ctk.CTkFrame):
    def __init__(self, parent, reg_number=None):
        super().__init__(parent, fg_color="#F4F6F9")
        self.reg_number = reg_number
        self.medicine_rows = [] 
        self.investigation_rows = []
        
        # --- 1. CONFIGURE STYLE FOR DROPDOWN ---
        # We use 'ttk' to get the scrollbar, but we style it to look modern
        style = ttk.Style()
        try:
            style.theme_use("clam") # 'clam' theme allows changing border colors
        except:
            pass # If system doesn't support clam, fallback to default

        # Define "Medical.TCombobox" style
        style.configure("Medical.TCombobox",
                        fieldbackground="white",       # Background inside the box
                        background="#6c757d",            # Background of the arrow button
                        foreground="#333",             # Text color
                        arrowcolor="#2c2c2c",          # Arrow icon color (Cyan)
                        bordercolor="#6c757d",         # Border color (Cyan)
                        lightcolor="#6c757d",          # 3D effect highlight (Cyan)
                        darkcolor="#6c757d")           # 3D effect shadow (Cyan)
        
        style.map("Medical.TCombobox",
                  fieldbackground=[("readonly", "white"), ("focus", "white")],
                  selectbackground=[("readonly", "white"), ("focus", "white")],
                  selectforeground=[("readonly", "#333"), ("focus", "#333")],
                  bordercolor=[("focus", "#6c757d")], # Cyan border when clicked
                  lightcolor=[("focus", "#6c757d")],
                  darkcolor=[("focus", "#6c757d")])
        
        # Fix for the popup listbox (The dropdown part)
        self.option_add('*TCombobox*Listbox.background', 'white')
        self.option_add('*TCombobox*Listbox.foreground', '#333')
        self.option_add('*TCombobox*Listbox.selectBackground', "#6c757d") # Selection color
        self.option_add('*TCombobox*Listbox.selectForeground', 'white')
        # ----------------------------------------

        # Load Medicines
        self.med_list = []
        try:
            with open("medicines.txt", "r") as f:
                self.med_list = [line.strip() for line in f.readlines() if line.strip()]
            self.med_list.sort()
        except FileNotFoundError:
            self.med_list = ["Error: medicines.txt not found"]
            
        # Add the Placeholder to the top of the list
        self.med_list.insert(0, "-- Select Medicine --")

        # ... (Rest of your __init__ code remains the same: SCROLLABLE CONTAINER etc.) ...
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        # ...
        self.card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=10, border_color="#d6d6d6", border_width=1)
        self.card.pack(fill="x", pady=(0, 20))
        
        self.history_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.history_frame.pack(fill="x", pady=(0, 20))

        self.form_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.form_frame.pack(fill="x")

        if not reg_number:
            self.show_search_bar()
        else:
            self.load_patient_card(reg_number)
            
            
    def show_search_bar(self):
        lbl = ctk.CTkLabel(self.card, text="Please select a patient from Dashboard.", font=("Arial", 14))
        lbl.pack(pady=20)

    def load_patient_card(self, reg_num):
        # A. Load Basic Info
        p_data = database.get_patient_by_reg(reg_num)
        if not p_data:
            messagebox.showerror("Error", "Patient not found")
            return

        # Clear previous widgets in card if any
        for widget in self.card.winfo_children():
            widget.destroy()

        # Row 1: Name & Reg
        r1 = ctk.CTkFrame(self.card, fg_color="transparent")
        r1.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(r1, text=p_data['name'], font=("Arial", 22, "bold"), text_color="#2cc985").pack(side="left")
        ctk.CTkLabel(r1, text=f"({p_data['reg']})", font=("Arial", 16, "bold"), text_color="#555").pack(side="left", padx=10)
        
        # Row 2: Details
        r2 = ctk.CTkFrame(self.card, fg_color="transparent")
        r2.pack(fill="x", padx=20, pady=(0, 15))
        details = f"Age: {p_data['age']}  |  Gender: {p_data['gender']}  |  Contact: {p_data['contact']}"
        ctk.CTkLabel(r2, text=details, font=("Arial", 12), text_color="#333").pack(side="left")
        ctk.CTkLabel(self.card, text=f"Address: {p_data['address']}", font=("Arial", 12), text_color="#555").pack(anchor="w", padx=20, pady=(0, 15))

        # B. Load History (Previous Treatments)
        self.load_history(reg_num)

        # C. Build Empty Form for New Treatment
        self.build_treatment_form()

    def load_history(self, reg_num):
        # 1. Clear previous history
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history_data = database.fetch_patient_history(reg_num)
        
        if not history_data:
            return

        # Title
        ctk.CTkLabel(self.history_frame, text="PREVIOUS TREATMENT HISTORY", 
                     font=("Arial", 14, "bold"), text_color="#555").pack(anchor="w", pady=(0, 10))

        # 2. Loop through visits
        for visit in history_data:
            # --- THE CARD CONTAINER ---
            # We use a border color to act as the outside border
            v_card = ctk.CTkFrame(self.history_frame, fg_color="white", 
                                  corner_radius=0, border_color="#d6d6d6", border_width=1)
            v_card.pack(fill="x", pady=10, padx=2)
            
            # CONFIGURE GRID:
            # Column 0: Labels (Fixed Width)
            # Column 1: Values (Expands)
            v_card.grid_columnconfigure(0, minsize=200, weight=0) 
            v_card.grid_columnconfigure(1, weight=1)

            # Variables to track grid rows
            current_row = 0

            # --- Helper Function for Grid Rows ---
            def add_grid_row(label_text, value_widget_func, is_last=False):
                nonlocal current_row
                
                # 1. LABEL (Column 0)
                # A frame is used to provide the Grey Background color
                lbl_frame = ctk.CTkFrame(v_card, fg_color="#2cc985", corner_radius=0)
                lbl_frame.grid(row=current_row, column=0, sticky="nsew")
                
                ctk.CTkLabel(lbl_frame, text=label_text, font=("Arial", 12, "bold"), 
                             text_color="#333").pack(anchor="w", padx=15, pady=12)

                # 2. VALUE (Column 1)
                # A frame for White Background
                val_frame = ctk.CTkFrame(v_card, fg_color="white", corner_radius=0)
                val_frame.grid(row=current_row, column=1, sticky="nsew")
                
                # Run the function passed to create the specific content (Text or Button)
                value_widget_func(val_frame)

                # 3. SEPARATOR LINE (Row + 1)
                if not is_last:
                    current_row += 1
                    line = ctk.CTkFrame(v_card, height=1, fg_color="#e0e0e0", corner_radius=0)
                    line.grid(row=current_row, column=0, columnspan=2, sticky="ew")
                    current_row += 1
                else:
                    current_row += 1

            # --- ROW 1: Treatment Date (Complex because of Delete Button) ---
            def date_content(parent):
                # Date Text
                ctk.CTkLabel(parent, text=visit['date'], font=("Arial", 12), text_color="#e74c3c").pack(side="left", padx=15, pady=12)
                # Delete Button
                del_btn = ctk.CTkButton(parent, text="× Delete", width=60, height=22, 
                                        fg_color="#f8d7da", text_color="#721c24", hover_color="#f1b0b7", 
                                        font=("Arial", 11))
                del_btn.pack(side="right", padx=15, pady=12)

            add_grid_row("Treatment Date", date_content)

            # --- ROW 2: Complaints ---
            def comp_content(parent):
                text = visit['complaints'] if visit['complaints'] else "-"
                ctk.CTkLabel(parent, text=text, font=("Arial", 12), text_color="#333", justify="left", anchor="w").pack(fill="x", padx=15, pady=12)
            
            add_grid_row("Complaints", comp_content)

            # --- ROW 3: Disease ---
            def dis_content(parent):
                text = visit['diagnosis'] if visit['diagnosis'] else "-"
                ctk.CTkLabel(parent, text=text, font=("Arial", 12), text_color="#333", anchor="w").pack(fill="x", padx=15, pady=12)

            add_grid_row("Disease", dis_content)

            # --- ROW 4: Medicines ---
            def med_content(parent):
                if visit['meds']:
                    med_lines = []
                    for m in visit['meds']:
                        med_lines.append(f"• {m[0]} ({m[1]})  —  {m[2]} for {m[3]}")
                    full_med_text = "\n".join(med_lines)
                else:
                    full_med_text = "No Medicines Prescribed"
                
                ctk.CTkLabel(parent, text=full_med_text, font=("Arial", 12), text_color="#333", 
                             justify="left", anchor="w").pack(fill="x", padx=15, pady=12)

            add_grid_row("Medicines", med_content)

            # --- ROW 5: Investigations ---
            def inv_content(parent):
                text = ", ".join([t[0] for t in visit['tests']]) if visit['tests'] else "-"
                ctk.CTkLabel(parent, text=text, font=("Arial", 12), text_color="#333", anchor="w").pack(fill="x", padx=15, pady=12)

            add_grid_row("Investigations", inv_content, is_last=True)

    def build_treatment_form(self):
        # Clear existing form
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # Reset lists
        self.medicine_rows = []
        self.investigation_rows = []

        # Title
        ctk.CTkLabel(self.form_frame, text="ADD NEW TREATMENT PLAN", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(10, 10))

        container = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=10)
        container.pack(fill="x")

        # --- Diagnosis Section ---
        diag_frame = ctk.CTkFrame(container, fg_color="transparent")
        diag_frame.pack(fill="x", pady=10)
        
        f_date = ctk.CTkFrame(diag_frame, fg_color="transparent")
        f_date.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_date, text="Date:", width=80, anchor="w").pack(side="left")
        self.entry_date = ctk.CTkEntry(f_date, width=150)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.pack(side="left")

        f_dis = ctk.CTkFrame(diag_frame, fg_color="transparent")
        f_dis.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_dis, text="Diagnosis:", width=80, anchor="w").pack(side="left")
        self.entry_disease = ctk.CTkEntry(f_dis, width=400)
        self.entry_disease.pack(side="left")
        
        f_comp = ctk.CTkFrame(diag_frame, fg_color="transparent")
        f_comp.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_comp, text="Complaints:", width=80, anchor="w").pack(side="left")
        self.entry_complaints = ctk.CTkEntry(f_comp, width=400)
        self.entry_complaints.pack(side="left")

        # --- Medicine Section ---
        self.med_wrapper = ctk.CTkFrame(container, fg_color="#F9F9F9", corner_radius=5)
        self.med_wrapper.pack(fill="x", padx=15, pady=10)
        
        # Header
        head = ctk.CTkFrame(self.med_wrapper, fg_color="transparent", height=30)
        head.pack(fill="x", padx=5, pady=5)
        labels = ["Medicine Name", "Potency", "Frequency", "Duration"]
        widths = [250, 100, 150, 100]
        for txt, w in zip(labels, widths):
            ctk.CTkLabel(head, text=txt, font=("Arial", 11, "bold"), width=w, text_color="#555").pack(side="left", padx=5)

        self.med_rows_frame = ctk.CTkFrame(self.med_wrapper, fg_color="transparent")
        self.med_rows_frame.pack(fill="x", padx=5)
        
        self.add_medicine_row()
        ctk.CTkButton(self.med_wrapper, text="+ Add Medicine", width=120, fg_color="#6c757d", height=25, command=self.add_medicine_row).pack(anchor="w", padx=10, pady=10)

        # --- Investigation Section ---
        self.inv_wrapper = ctk.CTkFrame(container, fg_color="transparent")
        self.inv_wrapper.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.inv_wrapper, text="Lab Tests:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.inv_rows_frame = ctk.CTkFrame(self.inv_wrapper, fg_color="transparent")
        self.inv_rows_frame.pack(fill="x")
        
        self.add_investigation_row()
        ctk.CTkButton(self.inv_wrapper, text="+ Add Test", width=100, fg_color="#6c757d", height=25, command=self.add_investigation_row).pack(anchor="w", pady=5)

        # --- Save Button ---
        btn_save = ctk.CTkButton(self.form_frame, text="SAVE & ADD", fg_color="#28a745", height=40, font=("Arial", 14, "bold"), command=self.save_data)
        btn_save.pack(fill="x", pady=20)

    def add_medicine_row(self):
        row_frame = ctk.CTkFrame(self.med_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5) # Increased padding slightly
        
        # --- MEDICINE DROPDOWN (Styled) ---
        # style="Medical.TCombobox" applies the colors defined in __init__
        c_name = ttk.Combobox(row_frame, values=self.med_list, 
                              width=35, height=15, 
                              font=("Arial", 11),
                              style="Medical.TCombobox")
        
        c_name.set("-- Select Medicine --") # Set Placeholder
        c_name.pack(side="left", padx=5, ipady=3)
        
        # Standard CTk ComboBoxes for the smaller fields (They look fine as is)
        c_pot = ctk.CTkComboBox(row_frame, values=["N/A", "250mg", "500mg", "650mg", "30CH", "200CH"], width=100)
        c_pot.pack(side="left", padx=5)
        
        c_freq = ctk.CTkComboBox(row_frame, values=["1-0-1", "1-1-1", "1-0-0", "0-0-1", "SOS", "Every 4 hrs"], width=150)
        c_freq.pack(side="left", padx=5)
        
        c_dur = ctk.CTkComboBox(row_frame, values=["3 Days", "5 Days", "7 Days", "15 Days", "1 Month"], width=100)
        c_dur.pack(side="left", padx=5)
        
        self.medicine_rows.append({"name": c_name, "potency": c_pot, "freq": c_freq, "duration": c_dur})

    def add_investigation_row(self):
        row_frame = ctk.CTkFrame(self.inv_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        c_test = ctk.CTkComboBox(row_frame, values=["Blood Test (CBC)", "X-Ray", "Sugar Test", "Typhoid", "Lipid Profile"], width=250)
        c_test.set("")
        c_test.pack(side="left", padx=0)
        
        e_note = ctk.CTkEntry(row_frame, placeholder_text="Notes/Results", width=300)
        e_note.pack(side="left", padx=10)
        
        self.investigation_rows.append({"test": c_test, "note": e_note})

    def save_data(self):
        if not self.reg_number:
            return
            
        date = self.entry_date.get()
        disease = self.entry_disease.get()
        complaints = self.entry_complaints.get()
        
        med_data = []
        for row in self.medicine_rows:
            name = row['name'].get()
            if name.strip():
                med_data.append({'name': name, 'potency': row['potency'].get(), 'freq': row['freq'].get(), 'duration': row['duration'].get()})
                
        inv_data = []
        for row in self.investigation_rows:
            test = row['test'].get()
            if test.strip():
                inv_data.append({'test': test, 'notes': row['note'].get()})
                
        success, msg = database.save_treatment(self.reg_number, date, complaints, disease, med_data, inv_data)
        
        if success:
            messagebox.showinfo("Success", "Treatment Prescribed Successfully!")
            # Reload the page to show the new history item immediately
            self.load_patient_card(self.reg_number)
        else:
            messagebox.showerror("Error", msg)