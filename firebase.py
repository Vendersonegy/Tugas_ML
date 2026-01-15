import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

# Path untuk penggunaan lokal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

def initialize_firebase():
    """
    Inisialisasi Firebase dengan dukungan Streamlit Secrets (Cloud) 
    dan file JSON (Lokal).
    """
    if not firebase_admin._apps:
        # 1. Coba inisialisasi menggunakan Streamlit Secrets (untuk Cloud)
        if "firebase" in st.secrets:
            try:
                # Mengambil data dari [firebase] di Secrets TOML
                secret_dict = dict(st.secrets["firebase"])
                
                # Pembersihan kunci privat agar format PEM valid
                if "private_key" in secret_dict:
                    # Menghapus spasi dan memperbaiki karakter newline
                    pk = secret_dict["private_key"].strip().replace("\\n", "\n")
                    secret_dict["private_key"] = pk
                
                cred = credentials.Certificate(secret_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                # Menampilkan error di sidebar agar tidak mengganggu layout utama
                st.sidebar.error(f"Gagal inisialisasi Secrets: {e}")

        # 2. Coba inisialisasi menggunakan file JSON (untuk Lokal)
        if os.path.exists(KEY_PATH):
            try:
                cred = credentials.Certificate(KEY_PATH)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.sidebar.error(f"Gagal inisialisasi File Lokal: {e}")
        
        return None
    
    # Jika sudah pernah diinisialisasi sebelumnya
    return firestore.client()

# Variabel global Database
db = initialize_firebase()

def save_detection_result(data):
    """Menyimpan data hasil deteksi ke Firestore"""
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return False
            
    try:
        db.collection("pelanggaran").add(data)
        return True
    except Exception as e:
        print(f"Error simpan data: {e}")
        return False

def get_all_detections():
    """Mengambil semua data riwayat deteksi"""
    global db
    if db is None:
        db = initialize_firebase()
        if db is None: return []
    
    try:
        docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        results = []
        for doc in docs:
            results.append(doc.to_dict())
        return results
    except Exception as e:
        print(f"Error ambil data: {e}")
        return []
    

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