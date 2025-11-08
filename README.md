# Tugas_ML
Proyek ini merupakan demonstrasi aplikasi Machine Learning berbasis Python yang menggunakan model AI untuk melakukan analisis dan prediksi data.
Aplikasi terintegrasi dengan Firebase untuk penyimpanan dan sinkronisasi data secara real-time menggunakan Firebase Admin SDK.
Video demo menunjukkan seluruh proses mulai dari instalasi library, setup environment, konfigurasi API key Firebase, hingga menjalankan fungsi utama aplikasi.

Anggota Kelompok
1.Jordan (221111018)
2.Sanjaya Citra (221111926)
3.Venderson Egy Agatran (221110627)

URL Aplikasi Live:


Petunjuk Penggunaan Aplikasi
1. Buka aplikasi melalui URL di atas atau jalankan secara lokal.
2. Pilih dataset atau input data yang ingin dianalisis.
3. Tekan tombol “Run Prediction” untuk menjalankan model AI.
4. Hasil prediksi akan muncul di layar dan otomatis tersimpan di Firebase.
5. Log aktivitas dapat dilihat di Firebase Console pada bagian Firestore Database.

Petunjuk Instalasi & Menjalankan di Lokal
1. Clone Repository
git clone https://github.com/Vendersonegy/Tugas_ML.git
cd Tugas_ML
3. Buat Virtual Environment
python -m venv venv
venv\Scripts\activate (Windows)
4. Instal Library yang Diperlukan
pip install -r requirements.txt
5. Jalankan Streamlit
streamlit run app.py
CATATAN PENTING : simpan best.pt di dalam folder model

