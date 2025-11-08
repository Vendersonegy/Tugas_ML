import cv2
import os
import uuid
from ultralytics import YOLO

# ======================
# LOAD YOLO MODEL
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f" Model YOLO tidak ditemukan di: {MODEL_PATH}")

print(f"[INFO] Memuat model dari: {MODEL_PATH}")
model = YOLO(MODEL_PATH)


# ======================
# DETEKSI VIDEO
# ======================
def run_detection(video_path, frame_skip=10, max_frames=100):
    """
    Jalankan deteksi YOLO pada video.
    - frame_skip: lewati beberapa frame agar cepat
    - max_frames: batasi jumlah frame untuk efisiensi
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video tidak ditemukan: {video_path}")

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    results_data = []

    output_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count > max_frames:
            break

        # proses hanya setiap n frame
        if frame_count % frame_skip == 0:
            results = model(frame)
            annotated = results[0].plot()

            filename = f"detect_{uuid.uuid4().hex[:8]}.jpg"
            out_path = os.path.join(output_dir, filename)
            cv2.imwrite(out_path, annotated)

            results_data.append({
                "frame_id": frame_count,
                "image_path": out_path,
            })

        frame_count += 1

    cap.release()
    print(f"[DONE] Frame diproses: {frame_count}, hasil deteksi: {len(results_data)}")
    return results_data
