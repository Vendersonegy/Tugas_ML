import cv2
import os
import uuid
from ultralytics import YOLO
from datetime import datetime
from plate_reader import read_plate
from firebase import save_detection_result

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best (2).pt")

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")

def calculate_evidence_score(yolo_conf, ocr_conf, frame_count):
    score = (yolo_conf * 40 + ocr_conf * 40 + min(frame_count / 100, 5) * 4)
    return round(min(score, 100), 2)

def run_detection(video_path, frame_skip=5, max_frames=300):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    detections = []

    # Pastikan folder outputs ada di direktori project
    output_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count > max_frames:
            break

        if frame_count % frame_skip == 0:
            results = model(frame)
            
            if len(results[0].boxes) > 0:
                # Mengambil frame yang sudah di-render dengan kotak deteksi
                annotated_frame = results[0].plot() 
                
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    plate_crop = frame[y1:y2, x1:x2]
                    yolo_conf = float(box.conf[0])
                    
                    plate_text, ocr_conf = read_plate(plate_crop)
                    
                    # Logika minimal 6 karakter
                    if len(plate_text) < 6:
                        plate_text = "TIDAK TERBACA"
                    
                    # Membuat nama file unik
                    filename = f"detect_{uuid.uuid4().hex[:8]}.jpg"
                    # Path relatif seringkali lebih aman untuk Streamlit
                    relative_path = os.path.join("outputs", filename)
                    full_path = os.path.join(BASE_DIR, relative_path)

                    # Simpan gambar
                    cv2.imwrite(full_path, annotated_frame)

                    evidence_score = calculate_evidence_score(yolo_conf, ocr_conf, frame_count)

                    data = {
                        "frame_id": frame_count,
                        "video_source": os.path.basename(video_path),
                        "image_path": full_path, # Path absolut untuk OS
                        "relative_path": relative_path, # Path relatif untuk Streamlit UI
                        "plate_number": plate_text,
                        "yolo_conf": round(yolo_conf, 3),
                        "ocr_conf": round(ocr_conf, 3),
                        "evidence_score": evidence_score,
                        "timestamp": datetime.now()
                    }

                    save_detection_result(data)
                    detections.append(data)

        frame_count += 1

    cap.release()
    return detections

# import cv2
# import os
# import uuid
# from ultralytics import YOLO
# from datetime import datetime
# from plate_reader import read_plate
# from firebase import save_detection_result

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "model", "best (2).pt")

# try:
#     model = YOLO(MODEL_PATH)
# except Exception as e:
#     print(f"Error loading model: {e}")

# def calculate_evidence_score(yolo_conf, ocr_conf, frame_count):
#     score = (yolo_conf * 40 + ocr_conf * 40 + min(frame_count / 100, 5) * 4)
#     return round(min(score, 100), 2)

# def run_detection(video_path, frame_skip=5, max_frames=300):
#     cap = cv2.VideoCapture(video_path)
#     frame_count = 0
#     detections = []
#     output_dir = os.path.join(BASE_DIR, "outputs")
#     os.makedirs(output_dir, exist_ok=True)

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret or frame_count > max_frames:
#             break

#         if frame_count % frame_skip == 0:
#             results = model(frame)
#             if len(results[0].boxes) > 0:
#                 annotated_frame = results[0].plot() 
                
#                 for box in results[0].boxes:
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     plate_crop = frame[y1:y2, x1:x2]
#                     yolo_conf = float(box.conf[0])
#                     plate_text, ocr_conf = read_plate(plate_crop)
                    
#                     if len(plate_text) < 6:
#                         plate_text = "TIDAK TERBACA"
                    
#                     filename = f"detect_{uuid.uuid4().hex[:8]}.jpg"
#                     relative_path = os.path.join("outputs", filename)
#                     full_path = os.path.join(BASE_DIR, relative_path)

#                     cv2.imwrite(full_path, annotated_frame)
#                     evidence_score = calculate_evidence_score(yolo_conf, ocr_conf, frame_count)

#                     data = {
#                         "frame_id": frame_count,
#                         "video_source": os.path.basename(video_path),
#                         "image_path": full_path,
#                         "relative_path": relative_path,
#                         "plate_number": plate_text,
#                         "yolo_conf": round(yolo_conf, 3),
#                         "ocr_conf": round(ocr_conf, 3),
#                         "evidence_score": evidence_score,
#                         "timestamp": datetime.now()
#                     }

#                     # OPTIMASI: Hanya simpan ke Firebase jika plat terbaca
#                     # Ini akan sangat menghemat kuota Write Anda
#                     if plate_text != "TIDAK TERBACA":
#                         save_detection_result(data)
                    
#                     detections.append(data)
#         frame_count += 1

#     cap.release()
#     return detections