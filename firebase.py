import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

# Path untuk penggunaan lokal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

def initialize_firebase():
    if not firebase_admin._apps:
        # 1. Coba baca dari Streamlit Secrets (untuk Cloud)
        if "firebase" in st.secrets:
            try:
                # Mengambil data [firebase] dari Secrets TOML
                secret_dict = dict(st.secrets["firebase"])
                # Memperbaiki format private_key jika ada error newline
                if "private_key" in secret_dict:
                    secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
                
                cred = credentials.Certificate(secret_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.error(f"Gagal inisialisasi Firebase dari Secrets: {e}")

        # 2. Coba baca dari File JSON (untuk Lokal)
        if os.path.exists(KEY_PATH):
            try:
                cred = credentials.Certificate(KEY_PATH)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.error(f"Gagal inisialisasi Firebase dari File: {e}")
        
        # Jika keduanya gagal
        st.warning("Kunci Firebase tidak ditemukan di Secrets maupun Lokal. Database dinonaktifkan.")
        return None
    
    return firestore.client()

# Inisialisasi Database
db = initialize_firebase()

def save_detection_result(data):
    # Simpan langsung ke Firestore tanpa upload cloud
    # Pastikan data["image_path"] berisi path absolut yang benar
    db.collection("pelanggaran").add(data)
    return True

def get_all_detections():
    # Menambahkan pengurutan agar data terbaru muncul di atas
    docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    results = []
    for doc in docs:
        results.append(doc.to_dict())
    return results

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