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
    
