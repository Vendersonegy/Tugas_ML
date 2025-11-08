import firebase_admin
from firebase_admin import credentials, firestore

# Inisialisasi Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("tugas-susah-firebase-adminsdk-fbsvc-c48e87a714.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
collection = db.collection("pelanggaran")

def save_detection_result(data):
    """Simpan metadata pelanggaran ke Firestore"""
    collection.add(data)
    return True

def get_all_detections():
    """Ambil semua data pelanggaran"""
    docs = collection.stream()
    results = []
    for doc in docs:
        results.append(doc.to_dict())
    return results
