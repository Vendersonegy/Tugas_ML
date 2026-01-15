# import firebase_admin
# from firebase_admin import credentials, firestore
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

# if not os.path.exists(KEY_PATH):
#     raise FileNotFoundError(
#         "firebase-key.json not found. "
#     )

# if not firebase_admin._apps:
#     cred = credentials.Certificate(KEY_PATH)
#     firebase_admin.initialize_app(cred)

# db = firestore.client()

# def save_detection_result(data):
#     db.collection("pelanggaran").add(data)
#     return True

# def get_all_detections():
#     docs = db.collection("pelanggaran").stream()
#     results = []
#     for doc in docs:
#         results.append(doc.to_dict())
#     return results

import firebase_admin
from firebase_admin import credentials, firestore
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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