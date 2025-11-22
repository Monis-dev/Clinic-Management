import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import database
from datetime import datetime
import webbrowser
import os

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, on_patient_click):
        super().__init__(parent, fg_color="#F4F6F9") 
        self.on_patient_click = on_patient_click 
        
        # =================================================================
        # 1. TOP SECTION: FILTER DATA
        # =================================================================
        self.filter_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=3, border_color="#d6d6d6", border_width=1)
        self.filter_frame.pack(fill="x", padx=15, pady=15)
        
        lbl_filter = ctk.CTkLabel(self.filter_frame, text="OPD - FILTER DATA", font=("Arial", 12), text_color="#555")
        lbl_filter.pack(anchor="w", padx=15, pady=(10,5))
        
        line = tk.Frame(self.filter_frame, height=1, bg="#eee")
        line.pack(fill="x", padx=5)
        
        self.inputs_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.inputs_frame.pack(fill="x", padx=10, pady=15)
        
        # From Date
        ctk.CTkLabel(self.inputs_frame, text="From", text_color="#333").pack(side="left", padx=(10, 5))
        self.date_from = ctk.CTkEntry(self.inputs_frame, placeholder_text="yyyy-mm-dd", width=120, height=30, fg_color="white", text_color="black", border_color="#ccc")
        self.date_from.pack(side="left")

        # To Date
        ctk.CTkLabel(self.inputs_frame, text="To", text_color="#333").pack(side="left", padx=(20, 5))
        self.date_to = ctk.CTkEntry(self.inputs_frame, placeholder_text="yyyy-mm-dd", width=120, height=30, fg_color="white", text_color="black", border_color="#ccc")
        self.date_to.pack(side="left")

        # Gender Filter
        ctk.CTkLabel(self.inputs_frame, text="Gender", text_color="#333").pack(side="left", padx=(20, 5))
        self.combo_gender = ctk.CTkComboBox(self.inputs_frame, values=["All", "Male", "Female", "Other"], width=150, height=30, fg_color="white", text_color="black", border_color="#ccc", button_color="#ddd")
        self.combo_gender.set("All")
        self.combo_gender.pack(side="left")
        
        # Filter Button (Connects to apply_filters)
        self.btn_filter = ctk.CTkButton(self.inputs_frame, text="🔍 Search", width=40, height=30, 
                                        fg_color="#17a2b8", hover_color="#138496", 
                                        font=("Arial", 12, "bold"),
                                        command=self.apply_filters)
        self.btn_filter.pack(side="left", padx=20)

        # =================================================================
        # 2. MIDDLE SECTION: HEADER & ACTIONS
        # =================================================================
        self.action_header = ctk.CTkFrame(self, fg_color="transparent")
        self.action_header.pack(fill="x", padx=15, pady=(0, 5))
        
        lbl_list = ctk.CTkLabel(self.action_header, text="PATIENTS LIST", font=("Arial", 14, "bold"), text_color="#333")
        lbl_list.pack(side="left")
        
        # View All
        btn_view_all = ctk.CTkButton(self.action_header, text="☰ VIEW ALL PATIENTS", width=120, height=30,
                                     fg_color="#fd7e14", hover_color="#e06b0d",
                                     command=self.load_data)
        btn_view_all.pack(side="right", padx=5)
        
        # Print Button (Connects to print_table)
        btn_print = ctk.CTkButton(self.action_header, text="🖨 PRINT", width=80, height=30,
                                  fg_color="#007bff", hover_color="#0069d9",
                                  command=self.print_table)
        btn_print.pack(side="right", padx=5)

        # =================================================================
        # 3. BOTTOM SECTION: TABLE CARD
        # =================================================================
        self.table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=3, border_color="#d6d6d6", border_width=1)
        self.table_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.ctrl_frame = ctk.CTkFrame(self.table_card, fg_color="white")
        self.ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.ctrl_frame, text="Show", text_color="#555").pack(side="left")
        self.combo_show = ctk.CTkComboBox(self.ctrl_frame, values=["10", "25", "50", "100", "All"], width=70, height=25, fg_color="white", text_color="black")
        self.combo_show.set("100")
        self.combo_show.pack(side="left", padx=5)
        ctk.CTkLabel(self.ctrl_frame, text="records", text_color="#555").pack(side="left")
        
        self.entry_search = ctk.CTkEntry(self.ctrl_frame, placeholder_text="Search...", width=200, height=30, fg_color="white", text_color="black", border_color="#ccc")
        self.entry_search.pack(side="right")
        ctk.CTkLabel(self.ctrl_frame, text="Search:", text_color="#555").pack(side="right", padx=5)

        # --- TREEVIEW ---
        self.tree_frame = ctk.CTkFrame(self.table_card, fg_color="white")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # STYLE: Force Grid Lines
        style = ttk.Style()
        style.theme_use("clam")
        
        # We add 'borderwidth' and 'relief' to the style to create lines
        style.configure("Treeview", 
                        background="white",
                        foreground="#333",
                        fieldbackground="white",
                        rowheight=40,
                        font=('Arial', 11))
        
        # This creates the visible border around every cell
        style.configure("Treeview.Item", borderwidth=1, bordercolor="#e0e0e0", relief="solid")
        
        style.configure("Treeview.Heading", 
                        background="#f8f9fa",
                        foreground="#333",
                        font=('Arial', 11, 'bold'),
                        borderwidth=1,
                        bordercolor="#d6d6d6",
                        relief="solid")
        
        style.map("Treeview", background=[("selected", "#007bff")], foreground=[("selected", "white")])

        columns = ("serial", "name", "reg_num", "date", "address", "gender", "type")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("serial", text="#")
        self.tree.heading("name", text="Name")
        self.tree.heading("reg_num", text="Reg No")
        self.tree.heading("date", text="Date")
        self.tree.heading("address", text="Address")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("type", text="Type")
        
        self.tree.column("serial", width=40, anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("reg_num", width=100)
        self.tree.column("date", width=100)
        self.tree.column("address", width=150)
        self.tree.column("gender", width=80)
        self.tree.column("type", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.on_row_double_click)
        self.entry_search.bind("<KeyRelease>", self.perform_search)

        self.load_data()

    def load_data(self):
        self.clear_table()
        data = database.fetch_all_patients() 
        self.populate_table(data)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_table(self, data):
        limit = self.combo_show.get()
        count = 0
        
        for idx, row in enumerate(data, start=1):
            # Safe unpacking
            # row structure: (id, reg, name, date, addr, type, gender, consultant)
            p_id = row[0]
            reg = row[1]
            name = row[2]
            date = row[3]
            addr = row[4]
            p_type = row[5]
            gender = row[6] if len(row) > 6 else "-"
            
            self.tree.insert("", "end", values=(idx, name, reg, date, addr, gender, p_type))
            
            count += 1
            if limit != "All" and count >= int(limit):
                break

    def perform_search(self, event=None):
        query = self.entry_search.get().lower()
        self.clear_table()
        
        all_data = database.fetch_all_patients()
        filtered_data = []
        
        for row in all_data:
            # Check name or reg number
            if query in row[1].lower() or query in row[2].lower():
                filtered_data.append(row)
        
        self.populate_table(filtered_data)

    def apply_filters(self):
        """Filters data based on Date Range and Gender"""
        date_from_str = self.date_from.get()
        date_to_str = self.date_to.get()
        gender_sel = self.combo_gender.get()

        self.clear_table()
        all_data = database.fetch_all_patients()
        filtered_data = []

        for row in all_data:
            # Row structure: (id, reg, name, date_str, addr, type, gender, consultant)
            row_date_str = row[3] # stored as YYYY-MM-DD in DB
            row_gender = row[6] if len(row) > 6 else ""

            # 1. Check Gender
            if gender_sel != "All" and gender_sel.lower() != row_gender.lower():
                continue

            # 2. Check Date Range
            # Only check if user actually entered dates
            include_row = True
            if date_from_str and date_to_str:
                try:
                    # Parse strings to dates for comparison
                    # Assuming DB date is YYYY-MM-DD
                    d_row = datetime.strptime(row_date_str, "%Y-%m-%d")
                    d_from = datetime.strptime(date_from_str, "%Y-%m-%d")
                    d_to = datetime.strptime(date_to_str, "%Y-%m-%d")
                    
                    if not (d_from <= d_row <= d_to):
                        include_row = False
                except ValueError:
                    # If date format is wrong, ignore date filter
                    pass
            
            if include_row:
                filtered_data.append(row)

        self.populate_table(filtered_data)

    def print_table(self):
        """Generates an HTML file of the current table and opens print dialog"""
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h2 { text-align: center; color: #333; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body onload="window.print()">
            <h2>Patient Report</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Name</th>
                        <th>Reg No</th>
                        <th>Date</th>
                        <th>Address</th>
                        <th>Gender</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Iterate through current treeview items (so it prints exactly what is filtered)
        for child in self.tree.get_children():
            values = self.tree.item(child)["values"]
            row_html = "<tr>"
            for v in values:
                row_html += f"<td>{v}</td>"
            row_html += "</tr>"
            html_content += row_html
            
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Save to temp file
        filename = "temp_print_view.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Open in default browser (which will trigger print)
        webbrowser.open(f"file://{os.path.realpath(filename)}")

    def on_row_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, 'values')
            reg_num = item_values[2] 
            self.on_patient_click(reg_num)