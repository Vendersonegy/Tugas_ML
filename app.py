import streamlit as st
import tempfile
import os
from detect import run_detection

# ===========================
# CONFIGURASI HALAMAN
# ===========================
st.set_page_config(page_title=" Deteksi Pelanggaran Lalu Lintas", layout="wide")
st.title(" Deteksi Pelanggaran Garis Putih & Lampu Merah")
st.write("Upload video untuk mendeteksi kendaraan yang melanggar lampu merah atau garis putih.")

st.sidebar.header(" Pengaturan")
st.sidebar.info("Upload video lalu klik tombol deteksi untuk menampilkan hasil deteksi YOLO.")

# ===========================
# UPLOAD VIDEO
# ===========================
uploaded = st.sidebar.file_uploader("📤 Upload video", type=["mp4", "avi", "mov"])
video_path = None

if uploaded:
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video.write(uploaded.read())
    video_path = temp_video.name
    st.sidebar.success(" Video berhasil diupload!")
    st.video(video_path)

# ===========================
# JALANKAN DETEKSI
# ===========================
if video_path and st.sidebar.button(" Jalankan Deteksi"):
    with st.spinner("Memproses video... Mohon tunggu..."):
        hasil = run_detection(video_path, frame_skip=10, max_frames=100)

    if hasil:
        st.success(f" Ditemukan {len(hasil)} hasil deteksi pelanggaran.")
        cols = st.columns(3)
        for i, data in enumerate(hasil):
            with cols[i % 3]:
                st.image(
                    data["image_path"],
                    caption=f"Frame {data['frame_id']}",
                    use_container_width=True
                )
    else:
        st.warning(" Tidak ada pelanggaran terdeteksi pada video ini.")

