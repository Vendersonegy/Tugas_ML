from ultralytics import YOLO
import cv2
import numpy as np
import os
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Callable
from firebase import save_detection_result  # 🔥 integrasi Firestore
import pytesseract

# ==============================
# KONFIGURASI
# ==============================
MODEL_PATH = "model/best.pt"
SAVE_DIR = "violations"
MIN_VEHICLE_CLASSES = {"car"}

# Parameter deteksi garis
CANNY_LOW = 50
CANNY_HIGH = 150
HOUGH_RHO = 1
HOUGH_THETA = np.pi / 180
HOUGH_THRESHOLD = 80
HOUGH_MINLEN = 100
HOUGH_MAXGAP = 20

# OCR
OCR_ENABLED = True
OCR_PSM = "--psm 7"

# Warna tampilan
COLOR_VIOLATION = (0, 0, 255)
COLOR_OK = (0, 255, 0)
COLOR_LINE = (255, 255, 255)
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX

# ==============================
# LOAD MODEL
# ==============================
model = YOLO(MODEL_PATH)

# ==============================
# HELPER FUNCTIONS
# ==============================
def is_vehicle(label: str) -> bool:
    return label.lower() in MIN_VEHICLE_CLASSES

def detect_lane_line(frame: np.ndarray) -> Optional[tuple]:
    """Mendeteksi garis horizontal (garis putih stop line)"""
    h, w = frame.shape[:2]
    crop = frame[int(h*0.35):h, :]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, CANNY_LOW, CANNY_HIGH)

    lines = cv2.HoughLinesP(edges, HOUGH_RHO, HOUGH_THETA, HOUGH_THRESHOLD,
                            minLineLength=HOUGH_MINLEN, maxLineGap=HOUGH_MAXGAP)
    if lines is None:
        return None

    best_line = None
    max_y = -1
    for l in lines:
        x1, y1, x2, y2 = l[0]
        y1 += int(h*0.35)
        y2 += int(h*0.35)
        if abs(y1 - y2) <= 30:  # hanya garis horizontal
            avg_y = (y1 + y2) / 2
            if avg_y > max_y:
                max_y = avg_y
                best_line = (int(x1), int(y1), int(x2), int(y2))
    return best_line

def crop_plate_from_vehicle(frame: np.ndarray, bbox: tuple) -> Optional[np.ndarray]:
    """Potong bagian bawah kendaraan untuk estimasi plat"""
    x1, y1, x2, y2 = bbox
    h = y2 - y1
    w = x2 - x1
    if h <= 0 or w <= 0:
        return None
    plate_y1 = int(y1 + 0.6 * h)
    plate_y2 = y2
    plate_x1 = int(x1 + 0.05 * w)
    plate_x2 = int(x2 - 0.05 * w)
    crop = frame[max(0, plate_y1):min(frame.shape[0], plate_y2),
                 max(0, plate_x1):min(frame.shape[1], plate_x2)]
    return crop

def ocr_plate_image(img: np.ndarray) -> str:
    """Membaca plat nomor pakai OCR"""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(th, config=OCR_PSM).strip()
        return "".join(ch for ch in text if ch.isalnum() or ch in ("-", " "))
    except Exception:
        return ""

def draw_annotations(frame: np.ndarray, boxes: List, names: dict, violator_boxes: List):
    """Gambar bounding box"""
    for box in boxes:
        xy = box.xyxy[0]
        x1, y1, x2, y2 = map(int, xy)
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        label = names.get(cls, str(cls))
        is_viol = any(np.allclose(box.xyxy[0], vb.xyxy[0]) for vb in violator_boxes)
        color = COLOR_VIOLATION if is_viol else COLOR_OK
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        txt = f"{label} {conf:.2f}"
        cv2.putText(frame, txt, (x1, max(y1 - 8, 10)), TEXT_FONT, 0.6, color, 2)
    return frame

# ==============================
# MAIN DETECTION FUNCTION
# ==============================
def run_detection(source_path: str,
                  save_dir: str = SAVE_DIR,
                  ocr_enabled: bool = OCR_ENABLED,
                  upload_callback: Optional[Callable[[str], str]] = None,
                  max_frames: Optional[int] = None
                  ) -> List[Dict]:

    os.makedirs(save_dir, exist_ok=True)
    ext = Path(source_path).suffix.lower()
    is_video = ext in [".mp4", ".avi", ".mov", ".mkv"]

    violations = []

    if is_video:
        cap = cv2.VideoCapture(source_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {source_path}")

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            if max_frames and frame_idx > max_frames:
                break

            lane = detect_lane_line(frame)
            results = model(frame)
            res = results[0]
            boxes = res.boxes
            names = model.names

            vehicle_boxes = [b for b in boxes if is_vehicle(names.get(int(b.cls[0]), ""))]

            violators = []
            if lane is not None:
                _, y1, _, y2 = lane
                lane_y = int((y1 + y2) / 2)
                for vb in vehicle_boxes:
                    x1, y1, x2, y2 = map(int, vb.xyxy[0])
                    center_y = (y1 + y2) // 2
                    if center_y > lane_y:  # lewat garis
                        violators.append(vb)

            if len(violators) > 0:
                frame_copy = frame.copy()
                cv2.line(frame_copy, (lane[0], lane[1]), (lane[2], lane[3]), COLOR_LINE, 3)
                frame_annot = draw_annotations(frame_copy, boxes, names, violators)

                out_name = f"viol_{uuid.uuid4().hex}.jpg"
                out_path = str(Path(save_dir) / out_name)
                cv2.imwrite(out_path, frame_annot)

                plate_text = ""
                vehicle_class = names.get(int(violators[0].cls[0]), "unknown")

                plate_crop = crop_plate_from_vehicle(frame, tuple(map(int, violators[0].xyxy[0])))
                if plate_crop is not None and ocr_enabled:
                    plate_text = ocr_plate_image(plate_crop)

                data = {
                    "id": uuid.uuid4().hex,
                    "class": vehicle_class,
                    "jenis_pelanggaran": "melanggar garis putih",
                    "plate": plate_text,
                    "image_path": out_path,
                }

                save_detection_result(data)

                violations.append(data)

        cap.release()

    return violations
