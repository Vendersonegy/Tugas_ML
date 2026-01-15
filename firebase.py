import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

# Path untuk penggunaan lokal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

def initialize_firebase():
    if not firebase_admin._apps:
        # 1. Coba dari Streamlit Secrets (Cloud)
        if "firebase" in st.secrets:
            try:
                secret_dict = dict(st.secrets["firebase"])
                if "private_key" in secret_dict:
                    secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(secret_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.error(f"Gagal inisialisasi Secrets: {e}")

        # 2. Coba dari File Lokal
        elif os.path.exists(KEY_PATH):
            try:
                cred = credentials.Certificate(KEY_PATH)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.error(f"Gagal inisialisasi File: {e}")
    
    # Jika sudah terinisialisasi sebelumnya
    elif firebase_admin._apps:
        return firestore.client()

    return None

# Global variable db
db = initialize_firebase()

def get_all_detections():
    """Mengambil semua data dengan proteksi AttributeError"""
    global db
    if db is None:
        # Coba inisialisasi ulang sekali lagi jika db masih None
        db = initialize_firebase()
        if db is None:
            return [] # Kembalikan list kosong jika tetap gagal
    
    try:
        docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        results = []
        for doc in docs:
            results.append(doc.to_dict())
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def save_detection_result(data):
    """Menyimpan data dengan proteksi AttributeError"""
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return False
        
    try:
        db.collection("pelanggaran").add(data)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
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