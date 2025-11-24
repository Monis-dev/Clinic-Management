import customtkinter as ctk
from tkinter import messagebox, ttk
import webbrowser
import os
import tempfile
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
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        p_date = database.get_patient_by_reg(reg_num)
        patient_reg_date = p_date['reg_date'] if p_date and 'reg_date' in p_date else "N/A"
        
        history_data = database.fetch_patient_history(reg_num)
        
        if not history_data:
            self.history_frame.pack_forget()
            return
        
        self.history_frame.pack(fill="x", pady=(0, 20), after=self.card)

        ctk.CTkLabel(self.history_frame, text="PREVIOUS TREATMENT HISTORY", 
                     font=("Arial", 14, "bold"), text_color="#555").pack(anchor="w", pady=(0, 10))

        for visit in history_data:
            
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
            
            
            create_cell(0, 0, "Reg Number", is_label=True)
            create_cell(0, 1, reg_num, text_color="#e74c3c")
            create_cell(0, 2, "Reg Date", is_label=True)
            create_cell(0, 3, patient_reg_date, text_color="#333")      
            
            create_cell(1, 0, "Treatment Date", is_label=True)
            create_cell(1, 1, visit["date"], text_color="#e74c3c")
            create_cell(1, 2, "Diagnosis", is_label=True)
            create_cell(1, 3, visit["diagnosis"])                    
            
            create_cell(2, 0, "Complaints", is_label=True)
            comp_text = visit['complaints'] if visit['complaints'] else "-"
            create_cell(2, 1, comp_text, colspan=3)

            create_cell(3, 0, "Medicines", is_label=True)
            
            if visit['meds']:
                med_lines = []
                for m in visit['meds']:
                    med_lines.append(f"• {m[0]} ({m[1]})  —  {m[2]} for {m[3]}")
                full_med_text = "\n".join(med_lines)
            else:
                full_med_text = "-"
                
            create_cell(3, 1, full_med_text, colspan=3)

            create_cell(4, 0, "Investigations", is_label=True)
            test_text = ", ".join([t[0] for t in visit['tests']]) if visit['tests'] else "-"
            create_cell(4, 1, test_text, colspan=3)

            footer = ctk.CTkFrame(v_card, fg_color="transparent", height=40)
            footer.pack(fill="x", pady=5)
            
            btn_print = ctk.CTkButton(footer, text="🖨 Print", width=80, height=28, 
                                      fg_color="#17a2b8", hover_color="#138496", font=("Arial", 11, "bold"), command=lambda v=visit: self.print_visit_card(p_date, v))
            btn_print.pack(side="right", padx=5)

            btn_del = ctk.CTkButton(footer, text="× Delete", width=80, height=28, 
                                    fg_color="#dc3545", hover_color="#c82333", font=("Arial", 11, "bold"))
            btn_del.pack(side="right", padx=5)

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
        
        c_name = ttk.Combobox(row_frame, values=self.med_list, 
                              width=35, height=15, 
                              font=("Arial", 11),
                              style="Medical.TCombobox")
        
        c_name.set("-- Select Medicine --") # Set Placeholder
        c_name.pack(side="left", padx=5, ipady=3)
        
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
            self.load_patient_card(self.reg_number)
        else:
            messagebox.showerror("Error", msg)
            
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