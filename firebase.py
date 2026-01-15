import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

_db = None

def init_firebase():
    global _db

    if firebase_admin._apps:
        _db = firestore.client()
        return _db

    try:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        return _db
    except Exception as e:
        print("Firebase init failed:", e)
        return None


def get_all_detections():
    global _db
    if _db is None:
        _db = init_firebase()
    if _db is None:
        return []

    docs = (
        _db.collection("pelanggaran")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def save_detection_result(data):
    global _db
    if _db is None:
        _db = init_firebase()
    if _db is None:
        return False

    _db.collection("pelanggaran").add(data)
    return True

    

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