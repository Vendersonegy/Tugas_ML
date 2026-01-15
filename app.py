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
    ["Deteksi Video", "Vehicle Frequency", "Repeat Offender dan Riwayat Data"]
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
elif menu == "Repeat Offender & Riwayat":
    st.title("🚨 Repeat Offender")

    if raw_data:
        df = pd.DataFrame(raw_data)
        df = df[df["plate_number"] != "TIDAK TERBACA"]

        repeat = df.groupby("plate_number").size().reset_index(name="Total Pelanggaran")
        repeat["Status"] = repeat["Total Pelanggaran"].apply(
            lambda x: "🚨 PRIORITAS" if x >= 3 else "Normal"
        )

        st.dataframe(repeat, use_container_width=True)

    st.divider()
    st.subheader("🧾 Riwayat Pelanggaran Valid")
    st.dataframe(df, use_container_width=True)


# import streamlit as st
# import pandas as pd
# import os
# from PIL import Image
# from detect import run_detection
# from firebase import get_all_detections

# st.set_page_config(
#     page_title="Sistem Deteksi Pelanggaran",
#     layout="wide"
# )

# # Sidebar Menu
# st.sidebar.title("🚦 Menu")
# menu = st.sidebar.radio(
#     "Pilih Fitur",
#     ["Deteksi Video", "Vehicle Frequency", "Repeat Offender dan Riwayat Data"]
# )

# @st.cache_data(ttl=60)
# def fetch_data():
#     return get_all_detections()

# raw_data = fetch_data()

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

#             # PEMISAHAN DATA
#             terbaca = [r for r in results if r.get('plate_number') != "TIDAK TERBACA"]
#             tidak_terbaca = [r for r in results if r.get('plate_number') == "TIDAK TERBACA"]

#             tab1, tab2 = st.tabs([f"✅ Terbaca ({len(terbaca)})", f"❌ Tidak Terbaca ({len(tidak_terbaca)})"])

#             # --- TAB 1: TERBACA ---
#             with tab1:
#                 if not terbaca:
#                     st.info("Tidak ada plat yang terbaca jelas (Min. 6 Karakter).")
#                 else:
#                     cols = st.columns(3)
#                     for idx, res in enumerate(terbaca):
#                         with cols[idx % 3]:
#                             st.write(f"**Frame: {res.get('frame_id', 0)}**")
                            
#                             # Cek Path Gambar
#                             img_path = res.get("image_path")
#                             if img_path and os.path.exists(img_path):
#                                 try:
#                                     img_file = Image.open(img_path)
#                                     st.image(img_file, use_column_width=True)
#                                 except Exception as e:
#                                     st.error(f"Gagal memuat gambar: {e}")
#                             else:
#                                 st.warning("🖼️ Gambar tidak ditemukan")

#                             # Styling Plat Kartu Hijau
#                             st.markdown(f"""
#                                 <div style="background-color: #1e3d2f; padding: 15px; border-radius: 0px 0px 10px 10px; border-left: 5px solid #4caf50; margin-top: -15px;">
#                                     <h4 style="color: white; margin: 0; font-size: 16px;">Plat: <span style="font-family: monospace; letter-spacing: 2px;">{res.get('plate_number')}</span></h4>
#                                 </div>
#                                 <br>
#                             """, unsafe_allow_html=True)

#             # --- TAB 2: TIDAK TERBACA ---
#             with tab2:
#                 if not tidak_terbaca:
#                     st.info("Semua plat terbaca.")
#                 else:
#                     cols = st.columns(3)
#                     for idx, res in enumerate(tidak_terbaca):
#                         with cols[idx % 3]:
#                             st.write(f"**Frame: {res.get('frame_id', 0)}**")
                            
#                             img_path = res.get("image_path")
#                             if img_path and os.path.exists(img_path):
#                                 try:
#                                     img_file = Image.open(img_path)
#                                     st.image(img_file, use_column_width=True)
#                                 except Exception as e:
#                                     st.error(f"Gagal memuat gambar: {e}")
#                             else:
#                                 st.warning("🖼️ Gambar tidak ditemukan")

#                             # Styling Plat Kartu Merah
#                             st.markdown(f"""
#                                 <div style="background-color: #3d1e1e; padding: 15px; border-radius: 0px 0px 10px 10px; border-left: 5px solid #f44336; margin-top: -15px;">
#                                     <h4 style="color: white; margin: 0; font-size: 16px;">❌ TIDAK TERBACA</h4>
#                                 </div>
#                                 <br>
#                             """, unsafe_allow_html=True)

# # ===============================
# # MODE 2 — VEHICLE FREQUENCY
# # ===============================
# elif menu == "Vehicle Frequency":
#     st.title("📊 Vehicle Frequency & Encounter Log")
#     if not raw_data:
#         st.warning("Belum ada data.")
#     else:
#         df = pd.DataFrame(raw_data)
#         df = df[df["plate_number"] != "TIDAK TERBACA"]

#         freq_df = df.groupby('plate_number').agg({
#             'video_source': 'nunique',
#             'timestamp': ['count', 'max']
#         }).reset_index()

#         freq_df.columns = ['Plat Nomor', 'Lokasi Berbeda', 'Total Muncul', 'Terakhir Terlihat']

#         st.subheader("🔝 Top 10 Kendaraan")
#         st.bar_chart(freq_df.set_index('Plat Nomor')['Total Muncul'].head(10))
#         st.dataframe(freq_df, use_container_width=True)

# # ===============================
# # MODE 3 — REPEAT OFFENDER
# # ===============================
# elif menu == "Repeat Offender dan Riwayat Data":
#     st.title("🚨 Pelanggar Berulang")
#     if raw_data:
#         df = pd.DataFrame(raw_data)
#         df = df[df["plate_number"] != "TIDAK TERBACA"]
#         repeat = df.groupby("plate_number").size().reset_index(name="total_pelanggaran")
#         repeat = repeat.sort_values("total_pelanggaran", ascending=False)

#         repeat["status"] = repeat["total_pelanggaran"].apply(
#             lambda x: "🚨 PRIORITAS" if x >= 3 else "Normal"
#         )

#         st.dataframe(repeat, use_container_width=True)

#     st.divider()
#     st.title("🧾 Riwayat Semua Pelanggaran")
#     if raw_data:
#         df = pd.DataFrame(raw_data)
#         df = df[df["plate_number"] != "TIDAK TERBACA"]

#         st.dataframe(df, use_container_width=True)
