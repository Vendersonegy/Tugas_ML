import streamlit as st
import pandas as pd
import os
from PIL import Image
from firebase import get_all_detections
from detect import run_detection

# Sidebar Menu
st.sidebar.title("🚦 Menu")
menu = st.sidebar.radio(
    "Pilih Fitur",
    ["Deteksi Video", "Vehicle Frequency", "Repeat Offender & Riwayat Data"]
)

@st.cache_data(ttl=60)
def fetch_data():
    try:
        data = get_all_detections()
        return data if data is not None else []
    except:
        return []

raw_data = fetch_data()

# Tampilkan peringatan jika database tidak terhubung
if not raw_data and menu != "Deteksi Video":
    st.sidebar.warning("⚠️ Database tidak terhubung atau data kosong.")

# ===============================
# MODE 1 — DETEKSI VIDEO
# ===============================
if menu == "Deteksi Video":
    st.title("🚦 Deteksi Pelanggaran Lalu Lintas")
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

    if uploaded_file:
        temp_path = "temp_video.mp4"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        if st.button("▶️ Jalankan Deteksi"):
            with st.spinner("Memproses video..."):
                results = run_detection(temp_path)
            
            st.success(f"Selesai! Total deteksi: {len(results)}")

            # PEMISAHAN DATA
            terbaca = [r for r in results if r.get('plate_number') != "TIDAK TERBACA"]
            tidak_terbaca = [r for r in results if r.get('plate_number') == "TIDAK TERBACA"]

            tab1, tab2 = st.tabs([f"✅ Terbaca ({len(terbaca)})", f"❌ Tidak Terbaca ({len(tidak_terbaca)})"])

            with tab1:
                if not terbaca:
                    st.info("Tidak ada plat yang terbaca jelas.")
                else:
                    cols = st.columns(3)
                    for idx, res in enumerate(terbaca):
                        with cols[idx % 3]:
                            img_path = res.get("relative_path") # Menggunakan path relatif
                            if img_path and os.path.exists(img_path):
                                st.image(Image.open(img_path), use_column_width=True)
                            st.write(f"**Plat: {res.get('plate_number')}**")

            with tab2:
                if not tidak_terbaca:
                    st.info("Semua plat terbaca.")
                else:
                    cols = st.columns(3)
                    for idx, res in enumerate(tidak_terbaca):
                        with cols[idx % 3]:
                            img_path = res.get("relative_path")
                            if img_path and os.path.exists(img_path):
                                st.image(Image.open(img_path), use_column_width=True)
                            st.write("❌ TIDAK TERBACA")

# ===============================
# MODE 2 — VEHICLE FREQUENCY
# ===============================
elif menu == "Vehicle Frequency":
    st.title("📊 Vehicle Frequency")

    if not raw_data:
        st.warning("Belum ada data.")
    else:
        df = pd.DataFrame(raw_data)
        df = df[df["plate_number"] != "TIDAK TERBACA"]

        freq = df.groupby("plate_number").size().reset_index(name="Total Muncul")
        st.bar_chart(freq.set_index("plate_number").head(10))
        st.dataframe(freq, use_container_width=True)

# ===============================
# MODE 3 — REPEAT OFFENDER & RIWAYAT
# ===============================
elif menu == "Repeat Offender & Riwayat Data":
    st.title("🚨 Repeat Offender")

    if not raw_data:
        st.warning("Belum ada data di database.")
    else:
        df = pd.DataFrame(raw_data)
        # Filter agar "TIDAK TERBACA" tidak masuk hitungan residivis
        df_filtered = df[df["plate_number"] != "TIDAK TERBACA"].copy()
        
        if df_filtered.empty:
            st.info("Belum ada data plat nomor yang terbaca.")
        else:
            # Hitung frekuensi
            repeat = df_filtered.groupby("plate_number").size().reset_index(name="total_pelanggaran")
            repeat = repeat.sort_values("total_pelanggaran", ascending=False)

            # Tambah status
            repeat["status"] = repeat["total_pelanggaran"].apply(
                lambda x: "🚨 PRIORITAS" if x >= 3 else "Normal"
            )

            st.dataframe(repeat, use_container_width=True)

            st.divider()
            st.title("🧾 Riwayat Semua Pelanggaran")
            # Menampilkan riwayat (bisa tampilkan df asli atau df_filtered)
            st.dataframe(df, use_container_width=True)

# import streamlit as st
# import pandas as pd
# import os
# from PIL import Image
# from firebase import get_all_detections
# from detect import run_detection

# st.set_page_config(page_title="Traffic Violation System", layout="wide")

# # Sidebar Menu
# st.sidebar.title("🚦 Menu")
# menu = st.sidebar.radio(
#     "Pilih Fitur",
#     ["Deteksi Video", "Vehicle Frequency", "Repeat Offender & Riwayat Data"]
# )

# # PENGHEMATAN KUOTA: Caching dan Session State
# @st.cache_data(ttl=600) # Data disimpan 10 menit
# def fetch_data_from_firebase():
#     return get_all_detections(limit=100) # Hanya ambil 100 data terbaru

# if "raw_data" not in st.session_state:
#     st.session_state.raw_data = fetch_data_from_firebase()

# # Tombol Refresh Manual di Sidebar
# if st.sidebar.button("🔄 Perbarui Data"):
#     st.cache_data.clear()
#     st.session_state.raw_data = fetch_data_from_firebase()
#     st.rerun()

# raw_data = st.session_state.raw_data

# # ===============================
# # MODE 1 — DETEKSI VIDEO
# # ===============================
# if menu == "Deteksi Video":
#     st.title("🚦 Deteksi Pelanggaran Lalu Lintas")
#     uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

#     if uploaded_file:
#         temp_path = "temp_video.mp4"
#         with open(temp_path, "wb") as f:
#             f.write(uploaded_file.read())

#         if st.button("▶️ Jalankan Deteksi"):
#             with st.spinner("Memproses video..."):
#                 results = run_detection(temp_path)
#             st.success(f"Selesai! Total deteksi: {len(results)}")
            
#             # Update data setelah deteksi selesai
#             st.cache_data.clear()
#             st.session_state.raw_data = fetch_data_from_firebase()

#             terbaca = [r for r in results if r.get('plate_number') != "TIDAK TERBACA"]
#             tidak_terbaca = [r for r in results if r.get('plate_number') == "TIDAK TERBACA"]
#             tab1, tab2 = st.tabs([f"✅ Terbaca ({len(terbaca)})", f"❌ Tidak Terbaca ({len(tidak_terbaca)})"])

#             with tab1:
#                 if not terbaca: st.info("Tidak ada plat yang terbaca jelas.")
#                 else:
#                     cols = st.columns(3)
#                     for idx, res in enumerate(terbaca):
#                         with cols[idx % 3]:
#                             img_path = res.get("relative_path")
#                             if img_path and os.path.exists(img_path):
#                                 st.image(Image.open(img_path), use_column_width=True)
#                             st.write(f"**Plat: {res.get('plate_number')}**")

# # ===============================
# # MODE 2 — VEHICLE FREQUENCY
# # ===============================
# elif menu == "Vehicle Frequency":
#     st.title("📊 Vehicle Frequency")
#     if not raw_data:
#         st.warning("Belum ada data (Coba klik 'Perbarui Data' di sidebar).")
#     else:
#         df = pd.DataFrame(raw_data)
#         df = df[df["plate_number"] != "TIDAK TERBACA"]
#         if not df.empty:
#             freq = df.groupby("plate_number").size().reset_index(name="Total Muncul")
#             st.bar_chart(freq.set_index("plate_number").head(10))
#             st.dataframe(freq, use_container_width=True)
#         else:
#             st.info("Tidak ada data plat terbaca.")

# # ===============================
# # MODE 3 — REPEAT OFFENDER
# # ===============================
# elif menu == "Repeat Offender & Riwayat Data":
#     st.title("🚨 Repeat Offender")
#     if not raw_data:
#         st.warning("Belum ada data.")
#     else:
#         df = pd.DataFrame(raw_data)
#         df_filtered = df[df["plate_number"] != "TIDAK TERBACA"].copy()
        
#         if df_filtered.empty:
#             st.info("Belum ada data plat nomor yang terbaca.")
#         else:
#             repeat = df_filtered.groupby("plate_number").size().reset_index(name="total_pelanggaran")
#             repeat = repeat.sort_values("total_pelanggaran", ascending=False)
#             repeat["status"] = repeat["total_pelanggaran"].apply(lambda x: "🚨 PRIORITAS" if x >= 3 else "Normal")
#             st.dataframe(repeat, use_container_width=True)

#             st.divider()
#             st.title("🧾 Riwayat Semua Pelanggaran")
#             st.dataframe(df, use_container_width=True)