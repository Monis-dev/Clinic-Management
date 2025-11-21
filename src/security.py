import base64
import uuid
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT = b'static_salt_doctor_app_2025'

def get_device_key():
    node = uuid.getnode()
    machine_id = str(node).encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=10000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(machine_id))
    return key

def encrypt_data(data):
    key = get_device_key()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token):
    try:
        key = get_device_key()
        f = Fernet(key)
        return f.decrypt(token.encode()).decode()
    except Exception:
        return "DATA CORRUPT OR WRONG DEVICE"