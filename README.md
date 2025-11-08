# Tugas_ML
Proyek ini merupakan demonstrasi aplikasi Machine Learning berbasis Python yang menggunakan model AI untuk melakukan Traffic Detection.
Aplikasi terintegrasi dengan Firebase untuk penyimpanan dan sinkronisasi data secara real-time menggunakan Firebase Admin SDK.
AI ini dibungkus menggunakan Framework Python Streamlit untuk memudahkan proses pembuatan Frontend serta integrasi library yang lancar dan kecepatan proses pengembangan yang signifikan.
Video demo menunjukkan seluruh proses mulai dari instalasi library, setup environment, konfigurasi API key Firebase, hingga menjalankan fungsi utama aplikasi.

Anggota Kelompok
1.Jordan (221111018)
2.Sanjaya Citra (221111926)
3.Venderson Egy Agatran (221110627)

Petunjuk Penggunaan Aplikasi
1. Buka aplikasi melalui URL di atas atau jalankan secara lokal.
2. Pilih video atau input url yang ingin dianalisis.
3. Tekan tombol “Run Prediction” untuk menjalankan model AI.
4. Hasil prediksi akan muncul di layar dan otomatis tersimpan di Firebase.
5. Log aktivitas dapat dilihat di Firebase Console pada bagian Firestore Database.

Petunjuk Instalasi & Menjalankan di Lokal
1. Clone Repository
git clone https://github.com/Vendersonegy/Tugas_ML.git
cd Tugas_ML
2. Instal Library yang Diperlukan
pip install -r requirements.txt
3. Jalankan Streamlit
streamlit run app.py

CATATAN PENTING : simpan best.pt di dalam folder model

🧠 Teknologi yang Digunakan
- Streamlit — membuat tampilan web interaktif dengan Python
- YOLOv8 (Ultralytics) — model deteksi objek real-time
- OpenCV — membaca dan menulis frame dari video
- Python — bahasa utama pengembangan
- Firebase	Menyimpan hasil deteksi secara online dan sinkronisasi data real-time
- NumPy & Torch	Mendukung operasi matematis dan inference YOLO di backend
