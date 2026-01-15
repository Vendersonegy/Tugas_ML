import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

# Path untuk penggunaan lokal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

def initialize_firebase():
    """Inisialisasi Firebase: Cek Secrets dulu (Cloud), lalu File (Lokal)"""
    if not firebase_admin._apps:
        # 1. Coba baca dari Streamlit Secrets (Cloud)
        if "firebase" in st.secrets:
            try:
                secret_dict = dict(st.secrets["firebase"])
                # Bersihkan karakter newline yang sering rusak di kunci RSA
                if "private_key" in secret_dict:
                    secret_dict["private_key"] = secret_dict["private_key"].strip().replace("\\n", "\n")
                
                cred = credentials.Certificate(secret_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                # Jangan print langsung, gunakan st.error agar terlihat di UI
                st.error(f"Gagal inisialisasi Firebase dari Secrets: {e}")

        # 2. Coba baca dari File Lokal (Lokal)
        if os.path.exists(KEY_PATH):
            try:
                cred = credentials.Certificate(KEY_PATH)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.error(f"Gagal inisialisasi Firebase dari File Lokal: {e}")
        
        # Jika semua metode gagal
        return None
    
    # Jika aplikasi sudah terinisialisasi sebelumnya
    return firestore.client()

# Variabel database global
db = initialize_firebase()

def save_detection_result(data):
    """Simpan data ke Firestore dengan proteksi NoneType"""
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return False
    try:
        db.collection("pelanggaran").add(data)
        return True
    except Exception as e:
        print(f"Error save: {e}")
        return False

def get_all_detections():
    """Ambil data dari Firestore dengan proteksi NoneType"""
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return []
    try:
        docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error fetch: {e}")
        return []

def save_detection_result(data):
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return False
    try:
        db.collection("pelanggaran").add(data)
        return True
    except:
        return False
    

# import firebase_admin
# from firebase_admin import credentials, firestore
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

# if not firebase_admin._apps:
#     cred = credentials.Certificate(KEY_PATH)
#     firebase_admin.initialize_app(cred)

# db = firestore.client()

# def save_detection_result(data):
#     # Simpan langsung ke Firestore tanpa upload cloud
#     # Pastikan data["image_path"] berisi path absolut yang benar
#     db.collection("pelanggaran").add(data)
#     return True

# def get_all_detections():
#     # Menambahkan pengurutan agar data terbaru muncul di atas
#     docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
#     results = []
#     for doc in docs:
#         results.append(doc.to_dict())
#     return results