# import cv2
# import easyocr
# import numpy as np

# reader = easyocr.Reader(['en'], gpu=False)

# def read_plate(img_crop):
#     if img_crop is None or img_crop.size == 0:
#         return "TIDAK TERDETEKSI", 0.0

#     try:
#         # 1. Grayscale & Upscaling
#         gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
#         gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

#         # 2. Bilateral Filter (Menghaluskan noise tapi menjaga tepi karakter tetap tajam)
#         gray = cv2.bilateralFilter(gray, 11, 17, 17)

#         # 3. Adaptive Thresholding (Lebih kuat daripada Otsu untuk cahaya tidak merata)
#         thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                       cv2.THRESH_BINARY, 11, 2)

#         # 4. OCR dengan allowlist dan paragraph=False agar tidak menggabung baris
#         results = reader.readtext(thresh, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        
#         if len(results) > 0:
#             # Ambil yang confidence-nya paling tinggi dalam satu crop
#             res = max(results, key=lambda x: x[2])
#             text = res[1].upper().replace(" ", "")
#             conf = res[2]
#             return text, conf
            
#     except Exception as e:
#         print(f"Error OCR: {e}")
        
#     return "TIDAK TERBACA", 0.0

import cv2
import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def read_plate(img_crop):
    if img_crop is None or img_crop.size == 0:
        return "TIDAK TERBACA", 0.0

    try:
        # Preprocessing Dasar
        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        # Perbesar 2x untuk meningkatkan detail karakter
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        
        # Adaptive Thresholding untuk menangani cahaya yang tidak rata
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)

        results = reader.readtext(thresh, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        
        if len(results) > 0:
            res = max(results, key=lambda x: x[2])
            text = res[1].upper().replace(" ", "")
            conf = res[2]
            
            # Jika confidence rendah atau karakter terlalu sedikit, anggap gagal
            if conf < 0.40 or len(text) < 3:
                return "TIDAK TERBACA", conf
                
            return text, conf
            
    except Exception as e:
        print(f"Error OCR: {e}")
        
    return "TIDAK TERBACA", 0.0
