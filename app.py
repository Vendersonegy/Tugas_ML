import streamlit as st
import tempfile
import os
import requests
from detect import run_detection
from firebase import get_all_detections

# Konfigurasi halaman
st.set_page_config(page_title=" Deteksi Pelanggaran Lalu Lintas", layout="wide")

# ==========================
# SIDEBAR - Firestore Data
# ==========================
st.sidebar.title("📋 Data Firestore")

if st.sidebar.button(" Tampilkan Semua Data"):
    with st.sidebar:
        with st.spinner("Mengambil data dari Firestore..."):
            all_data = get_all_detections()

        if not all_data:
            st.sidebar.info("Belum ada data pelanggaran yang tersimpan.")
        else:
            st.sidebar.success(f"Ditemukan {len(all_data)} data pelanggaran:")
            for i, d in enumerate(all_data, start=1):
                st.sidebar.markdown(f"###  Pelanggaran {i}")
                st.sidebar.json(d)

# ==========================
# MAIN PAGE
# ==========================
st.title(" Deteksi Pelanggaran Lalu Lintas")
st.write("Upload video untuk mendeteksi kendaraan yang melanggar garis putih atau lampu merah.")

# Input Video
st.header("Upload atau Masukkan URL Video")
metode_input = st.radio("Pilih metode input:", ["Upload Video", "URL Video"], horizontal=True)

video_path = None

# ---- Upload Video Langsung ----
if metode_input == "Upload Video":
    uploaded_file = st.file_uploader("Upload file video", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.write(uploaded_file.read())
        video_path = temp_video.name
        st.success(" Video berhasil diupload!")
        st.video(video_path)

# ---- Input URL Video ----
elif metode_input == "URL Video":
    video_url = st.text_input("Masukkan URL video (format langsung ke file .mp4):")
    if video_url:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        st.info(" Mengunduh video dari URL...")
        try:
            r = requests.get(video_url, stream=True)
            with open(temp_file.name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            video_path = temp_file.name
            st.success(" Video berhasil diunduh!")
            st.video(video_path)
        except Exception as e:
            st.error(f"Gagal mengunduh video: {e}")

# ==========================
# DETEKSI PELANGGARAN
# ==========================
if video_path:
    st.header(" Jalankan Deteksi")

    if st.button(" Mulai Deteksi"):
        with st.spinner("Memproses video... Mohon tunggu "):
            hasil = run_detection(video_path)

        if not hasil:
            st.warning(" Tidak ada pelanggaran terdeteksi.")
        else:
            st.success(f" Ditemukan {len(hasil)} pelanggaran!")

            for i, data in enumerate(hasil):
                st.image(data["image_path"], caption=f"Pelanggaran {i+1}")
                st.json(data)
