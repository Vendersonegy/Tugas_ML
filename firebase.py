import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

def initialize_firebase():
    if not firebase_admin._apps:
        # 1. Cek Streamlit Secrets (Cloud)
        if "firebase" in st.secrets:
            try:
                secret_dict = dict(st.secrets["firebase"])
                if "private_key" in secret_dict:
                    # Bersihkan karakter newline agar format PEM valid
                    pk = secret_dict["private_key"].strip().replace("\\n", "\n")
                    secret_dict["private_key"] = pk
                
                cred = credentials.Certificate(secret_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.sidebar.error(f"⚠️ Secrets Error: {e}")

        # 2. Cek File Lokal
        if os.path.exists(KEY_PATH):
            try:
                cred = credentials.Certificate(KEY_PATH)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            except Exception as e:
                st.sidebar.error(f"⚠️ File Error: {e}")
        
        return None
    return firestore.client()

db = initialize_firebase()

def get_all_detections():
    global db
    if db is None:
        db = initialize_firebase() # Proteksi AttributeError
        if db is None: return []
    try:
        docs = db.collection("pelanggaran").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except:
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