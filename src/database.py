import sqlite3
import bcrypt
from security import encrypt_data, decrypt_data

DB_NAME = 'clinic_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT
        )               
    ''') 
    conn.commit()
    conn.close()
    
def register_doctor(username, password, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(bytes, salt)
    
    enc_name = encrypt_data(full_name)
    
    try: 
        cursor.execute("INSERT INTO doctors (username, password_hash, full_name) VALUES (?, ?, ?)",
                       (username, hash_password.decode('utf-8'), enc_name))
        print("Successfully stored the info")
        conn.commit()
        return True, "Registration Successfull"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()
        
def login_doctor(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash, full_name FROM doctors WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_data = result[0] 
        enc_name = result[1]
        
        user_bytes = password.encode('utf-8')
        if isinstance(stored_data, str):
            stored_hash_bytes = stored_data.encode('utf-8')
        else:
            stored_hash_bytes = stored_data        
        if bcrypt.checkpw(user_bytes, stored_hash_bytes):
            real_name = decrypt_data(enc_name)
            if real_name == "DATA CORRUPT OR WRONG DEVICE" :
                return False, "Security Alert: Data belongs to another device."
            return True, real_name
        else:
            return False, "Invalid password"
    else:
        return False, "Username not found"
    
def create_patient_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Registration number is text to allow custom formats like "REG-2024-001"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_number TEXT UNIQUE,
            reg_date TEXT,
            name TEXT, 
            gender TEXT,
            age TEXT,
            address TEXT,
            contact TEXT,
            patient_type TEXT,
            consultant TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_patient(reg_num, reg_date, name, gender, age, address, contact, p_type, consultant):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Encrypt sensitive data
    enc_name = encrypt_data(name)
    enc_address = encrypt_data(address)
    enc_contact = encrypt_data(contact)
    
    try:
        cursor.execute('''
            INSERT INTO patients (reg_number, reg_date, name, gender, age, address, contact, patient_type, consultant)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reg_num, reg_date, enc_name, gender, age, enc_address, enc_contact, p_type, consultant))
        conn.commit()
        return True, "Patient Added Successfully"
    except sqlite3.IntegrityError:
        return False, "Registration Number already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def fetch_all_patients():
    """
    Fetches all patients including Gender and Consultant.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Added gender and consultant to the SELECT query
    cursor.execute("SELECT id, reg_number, reg_date, name, address, patient_type, gender, consultant FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    decrypted_rows = []
    for row in rows:
        try:
            p_id = row[0]
            reg = row[1]
            date = row[2]
            real_name = decrypt_data(row[3])
            real_addr = decrypt_data(row[4])
            p_type = row[5]
            gender = row[6]
            consultant = row[7]
            
            # Return tuple with all 8 items
            decrypted_rows.append((p_id, reg, real_name, date, real_addr, p_type, gender, consultant))
        except:
            continue 
            
    return decrypted_rows 

def delete_patient(reg_num):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
                    DELETE FROM patients WHERE reg_number = ?
                    ''', (reg_num,))
        conn.commit()
        return True, "Successfully remove the patient's data"
    except sqlite3.IntegrityError:
        return False, "Unable to find the patient registration number"
    except Exception as e:
        return False, f"Unable to delete patient data error:{e}"
    finally:
        conn.close()
    
        
def get_next_patient_id():
    """Returns the count of patients + 1 for ID generation"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0]
        return count + 1
    except:
        return 1
    finally:
        conn.close()    
                     
                     

def create_treatment_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Visits Table (Stores the main consultation info)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_number TEXT,
            visit_date TEXT,
            complaints TEXT,
            diagnosis TEXT
        )
    ''')
    
    # 2. Prescriptions Table (Linked to Visit)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER,
            medicine_name TEXT,
            potency TEXT,
            frequency TEXT,
            duration TEXT,
            FOREIGN KEY(visit_id) REFERENCES visits(visit_id)
        )
    ''')

    # 3. Investigations Table (Linked to Visit)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER,
            test_name TEXT,
            notes TEXT,
            FOREIGN KEY(visit_id) REFERENCES visits(visit_id)
        )
    ''')
    conn.commit()
    conn.close()

def get_patient_by_reg(reg_number):
    """Fetches a single patient's details and decrypts them"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE reg_number = ?", (reg_number,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try:
            return {
                "reg": row[1],
                "reg_date": row[2],
                "name": decrypt_data(row[3]),
                "age": row[5],
                "gender": row[4],
                "contact": decrypt_data(row[7]),
                "address": decrypt_data(row[6]),
                "consultant": row[9]
            }
        except:
            return None
    return None

def save_treatment(reg_num, date, complaints, diagnosis, medicines, investigations):
    """
    Saves the entire visit: 
    medicines is a list of dicts: [{'name': 'x', 'potency': 'y'...}]
    investigations is a list of dicts: [{'test': 'x'}]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # 1. Insert Visit
        cursor.execute("INSERT INTO visits (reg_number, visit_date, complaints, diagnosis) VALUES (?, ?, ?, ?)",
                       (reg_num, date, complaints, diagnosis))
        visit_id = cursor.lastrowid
        
        # 2. Insert Medicines
        for med in medicines:
            cursor.execute("INSERT INTO prescriptions (visit_id, medicine_name, potency, frequency, duration) VALUES (?, ?, ?, ?, ?)",
                           (visit_id, med['name'], med['potency'], med['freq'], med['duration']))
            
        # 3. Insert Investigations
        for inv in investigations:
            cursor.execute("INSERT INTO investigations (visit_id, test_name, notes) VALUES (?, ?, ?)",
                           (visit_id, inv['test'], inv['notes']))
                           
        conn.commit()
        return True, "Treatment Saved Successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
        
def fetch_patient_history(reg_number):
    """
    Returns a list of past visits. 
    Structure: [{'date': '...', 'diagnosis': '...', 'meds': [], 'tests': []}, ...]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Get all visits for this patient, ordered by latest first
    cursor.execute("SELECT visit_id, visit_date, complaints, diagnosis FROM visits WHERE reg_number = ? ORDER BY visit_id DESC", (reg_number,))
    visits_raw = cursor.fetchall()
    
    history = []
    
    for v in visits_raw:
        v_id = v[0]
        v_date = v[1]
        v_comp = v[2]
        v_diag = v[3]
        
        # 2. Get Medicines for this visit
        cursor.execute("SELECT medicine_name, potency, frequency, duration FROM prescriptions WHERE visit_id = ?", (v_id,))
        meds = cursor.fetchall() # List of tuples
        
        # 3. Get Investigations for this visit
        cursor.execute("SELECT test_name, notes FROM investigations WHERE visit_id = ?", (v_id,))
        tests = cursor.fetchall()
        
        history.append({
            "date": v_date,
            "complaints": v_comp,
            "diagnosis": v_diag,
            "meds": meds,
            "tests": tests
        })
        
    conn.close()
    return history
