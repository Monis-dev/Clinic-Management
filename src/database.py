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
                     