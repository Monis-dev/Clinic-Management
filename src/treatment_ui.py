import customtkinter as ctk
import webbrowser
import os
import tempfile
import database
import platform
import subprocess
import tkinter as tk

from tkinter import messagebox, ttk, filedialog
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
        
        style = ttk.Style()
        try:
            style.theme_use("clam") 
        except:
            pass 

        style.configure("Medical.TCombobox",
                        fieldbackground="white",      
                        background="#6c757d",        
                        foreground="#333",            
                        arrowcolor="#2c2c2c",        
                        bordercolor="#6c757d",       
                        lightcolor="#6c757d",        
                        darkcolor="#6c757d")         
        
        style.map("Medical.TCombobox",
                  fieldbackground=[("readonly", "white"), ("focus", "white")],
                  selectbackground=[("readonly", "white"), ("focus", "white")],
                  selectforeground=[("readonly", "#333"), ("focus", "#333")],
                  bordercolor=[("focus", "#6c757d")], 
                  lightcolor=[("focus", "#6c757d")],
                  darkcolor=[("focus", "#6c757d")])
        
        self.option_add('*TCombobox*Listbox.background', 'white')
        self.option_add('*TCombobox*Listbox.foreground', '#333')
        self.option_add('*TCombobox*Listbox.selectBackground', "#6c757d")
        self.option_add('*TCombobox*Listbox.selectForeground', 'white')
        # ----------------------------------------
        
        # other list 
        self.potency_list = ["N/A", "6C", "30C", "200C", "1M", "10M", "50M", "CM", "3X", "6X", "12X", "30X"]
        self.dur_list = ["3 Days", "5 Days", "7 Days", "15 Days", "1 Month"]
        self.freq_list = ["24 Hrly", "12 Hrly", "8 Hrly", "6 Hrly", "4 Hrly", "3 Hrly", "SOS", "Stat"]
        self.test_list = ["Blood Test (CBC)", "X-Ray", "Sugar Test", "Typhoid", "Lipid Profile"]
        
        # Medicine list
        self.med_list = []
        try:
            with open("medicines.txt", "r") as f:
                self.med_list = [line.strip() for line in f.readlines() if line.strip()]
            self.med_list.sort()
        except FileNotFoundError:
            self.med_list = ["Error: medicines.txt not found"]
            
        self.med_list.insert(0, "-- Select Medicine --")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=10, border_color="#d6d6d6", border_width=1)
        self.card.pack(fill="x", pady=(0, 20))
        
        self.history_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")

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

        # Clear previous widgets
        for widget in self.card.winfo_children():
            widget.destroy()

        # --- SECTION 1: BASIC DETAILS ---
        r1 = ctk.CTkFrame(self.card, fg_color="transparent")
        r1.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(r1, text=p_data['name'], font=("Arial", 22, "bold"), text_color="#2cc985").pack(side="left")
        ctk.CTkLabel(r1, text=f"({p_data['reg']})", font=("Arial", 16, "bold"), text_color="#555").pack(side="left", padx=10)
        
        r2 = ctk.CTkFrame(self.card, fg_color="transparent")
        r2.pack(fill="x", padx=20, pady=(0, 15))
        details = f"Age: {p_data['age']}  |  Gender: {p_data['gender']}  |  Contact: {p_data['contact']}"
        ctk.CTkLabel(r2, text=details, font=("Arial", 12), text_color="#333").pack(side="left")
        ctk.CTkLabel(self.card, text=f"Address: {p_data['address']}", font=("Arial", 12), text_color="#555").pack(anchor="w", padx=20, pady=(0, 15))

        # --- SECTION 2: PERSONAL HISTORY (Display Only if Exists) ---
        ph_data = database.get_personal_history(reg_num)
        has_real_data = ph_data and any(str(x).strip() for x in ph_data)
        
        if has_real_data:
            # Create a separator and container
            ctk.CTkFrame(self.card, height=1, fg_color="#e0e0e0").pack(fill="x", padx=10, pady=5)
            
            ph_frame = ctk.CTkFrame(self.card, fg_color="#f8f9fa", corner_radius=6)
            ph_frame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(ph_frame, text="PERSONAL HISTORY RECORD", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", padx=10, pady=(10, 5))
            
            # Labels list MUST match the order in the database SELECT query
            labels = [
                "Thermal", "Appetite", "Thirst", "Desire", "Aversion", 
                "Aggravation", "Amelioration", "Perspiration", "Sleep", "Stool", 
                "Urine", "Addiction", "Allergies", "Appearance", "Build", 
                "Height", "Weight", "Skin", "Hair Type", "Tongue", "Mental General"
            ]
            
            # Grid Container
            grid_box = ctk.CTkFrame(ph_frame, fg_color="transparent")
            grid_box.pack(fill="x", padx=10, pady=(0, 10))
            
            # Loop through data and display non-empty fields
            # We use a counter 'display_idx' to pack them neatly even if some are skipped
            display_idx = 0
            
            for i, value in enumerate(ph_data):
                if value and str(value).strip(): # Only show if value exists
                    
                    row = display_idx // 3 # 3 items per row
                    col = display_idx % 3
                    
                    # Cell Frame
                    cell = ctk.CTkFrame(grid_box, fg_color="white", corner_radius=4, border_width=1, border_color="#e0e0e0")
                    cell.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
                    grid_box.grid_columnconfigure(col, weight=1)
                    
                    # Label (Small Grey)
                    ctk.CTkLabel(cell, text=labels[i], font=("Arial", 9, "bold"), text_color="#888").pack(anchor="w", padx=8, pady=(4, 0))
                    # Value (Normal Black)
                    ctk.CTkLabel(cell, text=str(value), font=("Arial", 11), text_color="#333", wraplength=200).pack(anchor="w", padx=8, pady=(0, 4))
                    
                    display_idx += 1

        # B. Load History (Previous Treatments)
        self.load_history(reg_num)

        # C. Build Empty Form for New Treatment
        self.build_treatment_form()
        
        
    def load_history(self, reg_num):
        # 1. Clear previous history
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        p_data = database.get_patient_by_reg(reg_num)
        patient_reg_date = p_data['reg_date'] if p_data and 'reg_date' in p_data else "N/A"

        history_data = database.fetch_patient_history(reg_num)
        
        if not history_data:
            self.history_frame.pack_forget()
            return
        
        self.history_frame.pack(fill="x", pady=(0, 20), after=self.card)

        ctk.CTkLabel(self.history_frame, text="PREVIOUS TREATMENT HISTORY", 
                     font=("Arial", 14, "bold"), text_color="#555").pack(anchor="w", pady=(0, 10))

        # Calculate Total Visits to display "Visit #X" (assuming history_data is latest first)
        total_visits = len(history_data)

        for idx, visit in enumerate(history_data):
            
            # --- CALCULATE VISIT NUMBER ---
            # If list is [Latest, ..., Oldest], then Latest is visit #Total
            visit_num = total_visits - idx

            v_card = ctk.CTkFrame(self.history_frame, fg_color="white", corner_radius=0)
            v_card.pack(fill="x", pady=15, padx=2)

            grid_box = ctk.CTkFrame(v_card, fg_color="#d6d6d6", corner_radius=0)
            grid_box.pack(fill="x", expand=True)

            grid_box.grid_columnconfigure(0, weight=1, uniform="label") 
            grid_box.grid_columnconfigure(1, weight=2, uniform="value") 
            grid_box.grid_columnconfigure(2, weight=1, uniform="label") 
            grid_box.grid_columnconfigure(3, weight=2, uniform="value") 

            def create_cell(row, col, text, is_label=False, colspan=1, text_color="#333", bg_color=None):
                if bg_color:
                    cell_bg = bg_color
                else:
                    cell_bg = "#f9fafb" if is_label else "white"
                    
                font = ("Arial", 12, "bold") if is_label else ("Arial", 12)  
                
                cell = ctk.CTkFrame(grid_box, fg_color=cell_bg, corner_radius=0)
                cell.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=1, pady=1)
                
                lbl = ctk.CTkLabel(cell, text=text, font=font, text_color=text_color, anchor="w", justify="left")
                lbl.pack(fill="both", expand=True, padx=10, pady=8)
                return cell
            
            # --- ROW 0 ---
            create_cell(0, 0, "Reg Number", is_label=True)
            create_cell(0, 1, reg_num, text_color="#333") 
            
            create_cell(0, 2, "Reg Date", is_label=True)
            create_cell(0, 3, patient_reg_date, text_color="#333") 
            
            # --- ROW 1: Visit Number & Date ---
            create_cell(1, 0, f"Visit #{visit_num}", is_label=True, bg_color="#e3f2fd") # Light Blue
            create_cell(1, 1, visit["date"], text_color="#e74c3c") 
            
            create_cell(1, 2, "Diagnosis", is_label=True)
            create_cell(1, 3, visit["diagnosis"])                    
            
            # --- ROW 2: Complaints ---
            create_cell(2, 0, "Complaints", is_label=True)
            comp_text = visit['complaints'] if visit['complaints'] else "-"
            create_cell(2, 1, comp_text, colspan=3)

            # --- ROW 3: Medicines ---
            create_cell(3, 0, "Medicines", is_label=True)
            if visit['meds']:
                med_lines = []
                for m in visit['meds']:
                    med_lines.append(f"• {m[0]} ({m[1]})  —  {m[2]} for {m[3]}")
                full_med_text = "\n".join(med_lines)
            else:
                full_med_text = "-"
            create_cell(3, 1, full_med_text, colspan=3)

            # --- ROW 4: Investigations (CUSTOM CELL FOR FILE BUTTON) ---
            create_cell(4, 0, "Investigations", is_label=True)
            
            # Custom Cell logic for Value column
            inv_cell = ctk.CTkFrame(grid_box, fg_color="white", corner_radius=0)
            inv_cell.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=1, pady=1)
            
            if visit['tests']:
                # Create a mini list inside this cell
                for t in visit['tests']:
                    # t[0] is Name, t[1] is Notes/FilePath
                    test_name = t[0]
                    file_path = t[1]
                    
                    row_f = ctk.CTkFrame(inv_cell, fg_color="transparent")
                    row_f.pack(fill="x", padx=10, pady=2)
                    
                    ctk.CTkLabel(row_f, text=f"• {test_name}", font=("Arial", 12)).pack(side="left")
                    
                    # Check if file_path exists and is not empty
                    if file_path and os.path.exists(file_path):
                        # Add View Button
                        btn_v = ctk.CTkButton(row_f, text="👁 View File", width=70, height=22, 
                                              fg_color="#17a2b8", font=("Arial", 10),
                                              command=lambda p=file_path: self.open_file(p))
                        btn_v.pack(side="left", padx=10)
            else:
                 ctk.CTkLabel(inv_cell, text="-", font=("Arial", 12), anchor="w").pack(fill="x", padx=10, pady=8)

            # --- FOOTER ---
            footer = ctk.CTkFrame(v_card, fg_color="transparent", height=40)
            footer.pack(fill="x", pady=5)
            
            btn_print = ctk.CTkButton(footer, text="🖨 Print", width=80, height=28, 
                                      fg_color="#17a2b8", hover_color="#138496", font=("Arial", 11, "bold"),
                                      command=lambda p=p_data, v=visit: self.print_visit_card(p, v))
            btn_print.pack(side="right", padx=5)

            btn_del = ctk.CTkButton(footer, text="× Delete", width=80, height=28, 
                                    fg_color="#dc3545", hover_color="#c82333", font=("Arial", 11, "bold"), command=lambda v_id=visit["id"]: self.delete_treatment_plan(v_id))
            btn_del.pack(side="right", padx=5)
    
    def build_treatment_form(self):
        # ... (Clear widgets code) ...
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        self.medicine_rows = []
        self.investigation_rows = []
        
        history_exists = database.check_personal_history_exists(self.reg_number)
        
        # 1. INITIALIZE THE DICTIONARY
        self.ph_entries = {} 

        # ... (Header and Diagnosis Code stays the same) ...
        # (Copy your Diagnosis Date/Disease/Complaints part here)
        ctk.CTkLabel(self.form_frame, text="ADD NEW TREATMENT PLAN", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(10, 10))
        container = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=10)
        container.pack(fill="x")
        
        # Diagnosis Section
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

        # ==================================================
        # 2. PERSONAL HISTORY (The Fix)
        # ==================================================
        
        # Check if history exists (Optional, if you implemented that check)
        # history_exists = database.check_personal_history_exists(self.reg_number)
        if not history_exists:
            ph_wrapper = ctk.CTkFrame(container, fg_color="transparent")
            ph_wrapper.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(ph_wrapper, text="Personal History", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))

            # Define Labels
            field_labels = [
                "Thermal", "Appetite", "Thirst", 
                "Desire", "Aversion", "Aggravation", 
                "Amelioration", "Perspiration", "Sleep", 
                "Stool", "Urine", "Addiction", 
                "Allergies", "Appearance", "Build", 
                "Height", "Weight", "Skin", 
                "Hair Type", "Tongue", "Mental General"
            ]

            grid_frame = ctk.CTkFrame(ph_wrapper, fg_color="transparent")
            grid_frame.pack(fill="x")

            # Create fields in a loop
            for i, label_text in enumerate(field_labels):
                row = i // 3
                col = i % 3

                cell = ctk.CTkFrame(grid_frame, fg_color="transparent")
                cell.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                grid_frame.grid_columnconfigure(col, weight=1)

                ctk.CTkLabel(cell, text=label_text, font=("Arial", 11), anchor="w").pack(fill="x")

                entry = ctk.CTkEntry(cell, height=28)
                entry.pack(fill="x")

                # CRITICAL: Create the key and store the widget
                db_key = label_text.lower().replace(" ", "_")
                self.ph_entries[db_key] = entry  # <--- THIS IS WHAT WAS MISSING

        # ... (Rest of Medicine Section, unchanged) ...
        self.med_wrapper = ctk.CTkFrame(container, fg_color="#F9F9F9", corner_radius=5)
        self.med_wrapper.pack(fill="x", padx=15, pady=10)
        # (Add your Medicine UI code here: Headers, Add Button, etc)
        # ...
        self.med_rows_frame = ctk.CTkFrame(self.med_wrapper, fg_color="transparent")
        self.med_rows_frame.pack(fill="x", padx=5)
        self.add_medicine_row()
        ctk.CTkButton(self.med_wrapper, text="+ Add Medicine", width=120, fg_color="#6c757d", height=25, command=self.add_medicine_row).pack(anchor="w", padx=10, pady=10)

        # Investigation Section
        self.inv_wrapper = ctk.CTkFrame(container, fg_color="transparent")
        self.inv_wrapper.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.inv_wrapper, text="Lab Tests:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.inv_rows_frame = ctk.CTkFrame(self.inv_wrapper, fg_color="transparent")
        self.inv_rows_frame.pack(fill="x")
        self.add_investigation_row()
        ctk.CTkButton(self.inv_wrapper, text="+ Add Test", width=100, fg_color="#6c757d", height=25, command=self.add_investigation_row).pack(anchor="w", pady=5)

        # Save Button
        btn_save = ctk.CTkButton(self.form_frame, text="SAVE & ADD", fg_color="#28a745", height=40, font=("Arial", 14, "bold"), command=self.save_data)
        btn_save.pack(fill="x", pady=20)    
        
    def add_medicine_row(self):
        row_frame = ctk.CTkFrame(self.med_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5) 
        
        c_name = self.create_searchable_entry(row_frame, self.med_list, width=220, placeholder="Medicine Name")
        
        c_pot = self.create_searchable_entry(row_frame, self.potency_list, width=80, placeholder="Potency")
        
        c_freq = self.create_searchable_entry(row_frame, self.freq_list, width=120, placeholder="Frequency")
        
        c_dur = self.create_searchable_entry(row_frame, self.dur_list, width=100, placeholder="Duration")
        
        self.medicine_rows.append({
            "name": c_name, 
            "potency": c_pot, 
            "freq": c_freq, 
            "duration": c_dur
        })

    def add_investigation_row(self):
        row_frame = ctk.CTkFrame(self.inv_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        # 1. Test Name (Searchable)
        c_test = self.create_searchable_entry(row_frame, self.test_list, width=220, placeholder="Select Test")
        
        # 2. Notes Entry (Standard)
        e_note = ctk.CTkEntry(row_frame, placeholder_text="Result/Notes", width=200)
        e_note.pack(side="left", padx=5)

        # 3. File Label Box
        file_box = ctk.CTkFrame(row_frame, fg_color="white", width=120, height=28, border_width=1, border_color="#aaa")
        file_box.pack(side="left", padx=5)
        file_box.pack_propagate(False) 
        
        lbl_filename = ctk.CTkLabel(file_box, text="No file selected", font=("Arial", 10), text_color="gray")
        lbl_filename.place(relx=0.5, rely=0.5, anchor="center")

        # 4. View Button
        btn_view = ctk.CTkButton(row_frame, text="👁", width=35, height=28, fg_color="#ced4da", state="disabled")
        btn_view.pack(side="left", padx=(5, 2))

        # 5. Data & Upload Button
        row_data = {
            "test": c_test, 
            "note": e_note, 
            "file_path": None,
            "btn_view": btn_view 
        }

        btn_upload = ctk.CTkButton(row_frame, text="📂", width=35, height=28, fg_color="#6c757d", 
                                   command=lambda: self.select_file(lbl_filename, row_data))
        btn_upload.pack(side="left", padx=0)

        self.investigation_rows.append(row_data)

    def save_data(self):
        if not self.reg_number:
            messagebox.showwarning("Error", "No patient selected.")
            return

        date = self.entry_date.get()
        disease = self.entry_disease.get()
        complaints = self.entry_complaints.get()
        
        ph_data = {}
        for db_key, entry_widget in self.ph_entries.items():
            value = entry_widget.get()
            ph_data[db_key] = value
            
        # ... (Gather Medicines logic) ...
        med_data = []
        for row in self.medicine_rows:
            name = row['name'].get()
            if name and name != "-- Select Medicine --" and name.strip():
                med_data.append({
                    'name': name,
                    'potency': row['potency'].get(),
                    'freq': row['freq'].get(),
                    'duration': row['duration'].get()
                })

        inv_data = []
        for row in self.investigation_rows:
            test = row['test'].get()
            path = row.get('file_path') 
            if test.strip():
                note_to_save = path if path else ""
                inv_data.append({'test': test, 'notes': note_to_save})

        success, msg = database.save_treatment(
            self.reg_number, date, complaints, disease, med_data, inv_data, ph_data
        )
        
        if success:
            messagebox.showinfo("Success", "Saved!")
            self.load_patient_card(self.reg_number)
        else:
            messagebox.showerror("Error", msg)
       
    def delete_treatment_plan(self, visit_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this treatment plan?\nThis cannot be undone.")
        
        if confirm:
            success, msg = database.delete_visit(visit_id)
            
            if success:
                messagebox.showinfo("Success", msg)
                self.load_patient_card(self.reg_number)
            else:
                messagebox.showerror("Error", msg)   
                
                      
    def setup_autocomplete(self, entry_widget, data_list, arrow_button=None):
        # 1. Get the Main Window (Root)
        # We attach the listbox to the main window so it floats ABOVE everything else
        root = entry_widget.winfo_toplevel()
        
        # 2. Create a Frame to hold Listbox + Scrollbar
        pop_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
        
        # 3. Create Listbox & Scrollbar
        listbox = tk.Listbox(pop_frame, width=40, height=8, font=("Arial", 11), 
                             bd=0, highlightthickness=0, selectbackground="#17a2b8", selectforeground="white")
        listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(pop_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        listbox.config(yscrollcommand=scrollbar.set)
        
        # --- Helper to Position and Show ---
        def show_list(data):
            # Clear old data
            listbox.delete(0, 'end')
            for item in data:
                listbox.insert('end', item)
            
            if not data:
                pop_frame.place_forget()
                return

            # CALCULATE EXACT SCREEN POSITION
            # This ensures it appears exactly under the entry, even inside scrollable frames
            root_x = root.winfo_rootx()
            root_y = root.winfo_rooty()
            
            # Entry position relative to screen
            entry_x = entry_widget.winfo_rootx()
            entry_y = entry_widget.winfo_rooty()
            
            # Position relative to Root Window
            final_x = entry_x - root_x
            final_y = (entry_y - root_y) + entry_widget.winfo_height()
            
            pop_frame.place(x=final_x, y=final_y)
            pop_frame.lift() # Bring to front layer

        def hide_list():
            pop_frame.place_forget()

        # --- Event: Typing ---
        def check_key(event):
            typed = entry_widget.get()
            if typed == '':
                hide_list()
            else:
                # Case-insensitive search
                filtered = [i for i in data_list if typed.lower() in i.lower()]
                show_list(filtered)

        # --- Event: Selecting ---
        def on_select(event):
            if listbox.curselection():
                index = listbox.curselection()[0]
                selected_item = listbox.get(index)
                
                # Fill Entry
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, selected_item)
                hide_list()

        # --- Event: Arrow Button ---
        def toggle_dropdown():
            if pop_frame.winfo_viewable():
                hide_list()
            else:
                # If entry has text, filter. If empty, show ALL.
                typed = entry_widget.get()
                if typed:
                    filtered = [i for i in data_list if typed.lower() in i.lower()]
                    show_list(filtered)
                else:
                    show_list(data_list)
                
                entry_widget.focus_set()

        # Bindings
        entry_widget.bind('<KeyRelease>', check_key)
        listbox.bind('<<ListboxSelect>>', on_select)
        
        # Connect Arrow Button
        if arrow_button:
            arrow_button.configure(command=toggle_dropdown)
            
        # Optional: Close when clicking away (Advanced logic omitted for stability)
    
    def select_file(self, label_widget, row_data):
        filetypes = (
            ('Images', '*.png;*.jpg;*.jpeg'),
            ('PDF', '*.pdf'),
            ('All files', '*.*')
        )
        filepath = filedialog.askopenfilename(
            title='Report file',
            initialdir='/', 
            filetypes=filetypes
        )

        if filepath:
            row_data['file_path'] = filepath
            filename = os.path.basename(filepath)
            if len(filename) > 15:
                filename = filename[:12] + "..."
            label_widget.configure(text=filename, text_color="#2cc985")
            btn = row_data['btn_view']
            btn.configure(state="normal", fg_color="#17a2b8")
            btn.configure(command=lambda: self.open_file(filepath))
            print(f"Selected File: {filepath}")

        else:
            print("File selection cancelled.")
    
    def create_searchable_entry(self, parent_frame, data_list, width=150, placeholder=""):
        """
        Creates a Frame containing: [ Entry | ▼ Button ]
        And links it to the autocomplete logic.
        Returns the Entry widget.
        """
        # 1. Container Frame (keeps Entry and Button together)
        container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        container.pack(side="left", padx=5)

        # 2. Entry
        entry = ctk.CTkEntry(container, width=width, placeholder_text=placeholder)
        entry.pack(side="left", padx=0)
        
        # 3. Arrow Button
        btn = ctk.CTkButton(container, text="▼", width=25, height=28, 
                            fg_color="#e0e0e0", text_color="black", hover_color="#d6d6d6")
        btn.pack(side="left", padx=0)
        
        # 4. Connect Logic
        self.setup_autocomplete(entry, data_list, arrow_button=btn)
        
        return entry
    
    def open_file(self, filepath):
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "File not found")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
                print(f"Opening file: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the file: {e}")
       
    def print_visit_card(self, p_data, visit):
        """Generates an HTML file matching the Aarogyam Clinic reference"""
        
        # 1. Format Medicines
        med_rows_html = ""
        if visit['meds']:
            for m in visit['meds']:
                med_rows_html += f"""
                <tr>
                    <td class="label">Medicine</td>
                    <td colspan="3" style="font-weight:bold;">{m[0]}</td>
                </tr>
                <tr>
                    <td class="label">Potency</td>
                    <td>{m[1]}</td>
                    <td class="label">Frequency</td>
                    <td>{m[2]}</td>
                </tr>
                 <tr>
                    <td class="label">Duration</td>
                    <td colspan="3">{m[3]}</td>
                </tr>
                <tr><td colspan="4" style="border:none; height:5px;"></td></tr>
                """
        else:
            med_rows_html = '<tr><td class="label">Medicine</td><td colspan="3">-</td></tr>'

        # 2. Format Investigations
        test_text = ", ".join([t[0] for t in visit['tests']]) if visit['tests'] else "-"

        # 3. Prepare Data for the Top Form
        # We handle missing keys gracefully since we might not have Weight/Email in DB
        name = p_data.get('name', '')
        age = p_data.get('age', '')
        gender = p_data.get('gender', '')
        reg_no = p_data.get('reg', '')
        contact = p_data.get('contact', '')
        date = visit['date']
        address = p_data.get('address', '')
        
        # HTML & CSS Construction
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription</title>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif; 
                    padding: 40px; 
                    max-width: 900px; 
                    margin: auto; 
                    color: #333;
                }}
                
                /* --- HEADER STYLES --- */
                .clinic-title {{
                    text-align: center;
                    font-size: 36px;
                    font-weight: bold;
                    color: #800000; /* Maroon Color */
                    margin-bottom: 5px;
                    text-shadow: 1px 1px 0px #ddd;
                }}
                
                .clinic-addr {{
                    text-align: center;
                    font-size: 14px;
                    color: #004d00; /* Dark Green */
                    margin-bottom: 10px;
                }}
                
                .divider-green {{
                    border-top: 2px solid #006400; /* Green Line */
                    margin: 10px 0;
                }}
                
                /* Doctors Section */
                .doctors-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }}
                
                .doc-box {{ width: 48%; }}
                .doc-right {{ text-align: right; }}
                
                .doc-name {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #800000; /* Maroon */
                }}
                
                .doc-deg {{ font-size: 12px; font-weight: bold; }}
                .doc-detail {{ font-size: 13px; color: #222; line-height: 1.4; }}
                
                /* Patient Form Section (The Input Lines) */
                .patient-form {{
                    margin-top: 15px;
                    font-size: 15px;
                    line-height: 1.8;
                }}
                
                .form-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }}
                
                /* Creates the "______" look with filled data */
                .field {{
                    border-bottom: 1px solid #800000; /* Maroon Underline */
                    padding: 0 10px;
                    color: #000;
                    font-weight: bold;
                    min-width: 50px;
                    display: inline-block;
                    text-align: center;
                }}
                
                .label-text {{ color: #004d00; font-weight: bold; }} /* Green Labels */
                
                /* --- TREATMENT TABLE STYLES --- */
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
                td {{ border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; }}
                .bg-label {{ background-color: #f9f9f9; width: 130px; font-weight: bold; color: #555; }}
                
            </style>
        </head>
        <body onload="window.print()">

            <!-- 1. CLINIC HEADER -->
            <div class="clinic-title">Aarogyam Homoeopathic Clinic</div>
            <div class="clinic-addr">
                UG-09, Royal View, FF-27-28, Sch. No. 54, Near South Indian Bank, Vijay Nagar, INDORE - 452010 (M.P.)
            </div>
            
            <div class="divider-green"></div>
            
            <!-- 2. DOCTORS SECTION -->
            <div class="doctors-row">
                <!-- Left Doctor -->
                <div class="doc-box">
                    <div class="doc-name">Dr. Rajesh Bordia</div>
                    <div class="doc-deg">M.D. (Hom.)</div>
                    <div class="doc-detail">Professor - S.K.R.P. Gujrati Homoeopathic Medical College</div>
                    <div class="doc-detail">Time : 6:30 - 9:00, Mob. : 98260-11330</div>
                </div>
                
                <!-- Right Doctor -->
                <div class="doc-box doc-right">
                    <div class="doc-name">Dr. Tanuja Bordia</div>
                    <div class="doc-deg">M.D. (Hom.)</div>
                    <div class="doc-detail">Homoeopathic Physician</div>
                    <div class="doc-detail">Time : 5:00 - 7:00, Mob. : 98260-11331</div>
                </div>
            </div>
            
            <div class="divider-green"></div>
            
            <!-- 3. PATIENT DETAILS FORM -->
            <div class="patient-form">
                <!-- Row 1 -->
                <div class="form-row">
                    <div>
                        <span class="label-text">Name of Patient :</span> 
                        <span class="field" style="width: 300px;">{name}</span>
                    </div>
                    <div>
                        <span class="label-text">Age & Sex :</span> 
                        <span class="field" style="width: 150px;">{age} / {gender}</span>
                    </div>
                    <div>
                        <span class="label-text">Regd. No.</span> 
                        <span class="field" style="width: 100px;">{reg_no}</span>
                    </div>
                </div>
                
                <!-- Row 2 -->
                <div class="form-row">
                    <div>
                        <span class="label-text">Occupation :</span> 
                        <span class="field" style="width: 180px;"></span> <!-- Empty for now -->
                    </div>
                    <div>
                        <span class="label-text">Contact No.</span> 
                        <span class="field" style="width: 150px;">{contact}</span>
                    </div>
                    <div>
                        <span class="label-text">Date :</span> 
                        <span class="field" style="width: 120px;">{date}</span>
                    </div>
                </div>
                
                <!-- Row 3 -->
                <div class="form-row">
                    <div style="width: 100%;">
                        <span class="label-text">Address :</span> 
                        <span class="field" style="width: 85%;">{address}</span>
                    </div>
                </div>
            </div>
            
            <div class="divider-green" style="border-top: 1px solid #ccc; margin-top: 15px;"></div>

            <!-- 4. TREATMENT DETAILS -->
            <h3 style="text-decoration: underline; text-align: center; margin-top: 20px;">PRESCRIPTION</h3>
            
            <table>
                <tr>
                    <td class="bg-label">Diagnosis</td>
                    <td colspan="3">{visit['diagnosis']}</td>
                </tr>
                <tr>
                    <td class="bg-label">Complaints</td>
                    <td colspan="3">{visit['complaints']}</td>
                </tr>
                
                <!-- Medicines -->
                {med_rows_html}

                <tr>
                    <td class="bg-label">Investigations</td>
                    <td colspan="3">{test_text}</td>
                </tr>
            </table>

        </body>
        </html>
        """
        
        # Save and Open
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            f.write(html_content.encode('utf-8'))
            temp_filename = f.name
            
        webbrowser.open(f"file://{os.path.realpath(temp_filename)}")