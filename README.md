# 🎮 FiveGames

**FiveGames** adalah aplikasi permainan sederhana berbasis Python dan Flet yang dirancang untuk dimainkan pada perangkat mobile. Aplikasi ini menyediakan lima permainan dengan jenis dan cara bermain yang berbeda, yaitu **Chess, Hangman, Maze, Minesweeper, dan Tic-Tac-Toe**.

FiveGames dibuat dengan tampilan sederhana agar pemain dapat langsung memilih permainan dan memainkannya tanpa proses yang rumit.

---

## 📖 Manual Book FiveGames

### 1. Memulai Permainan

Setelah aplikasi dibuka, pemain akan berada di **Menu Utama**.

Pada menu utama tersedia pilihan permainan yang dapat dipilih. Tekan permainan yang ingin dimainkan untuk masuk ke halaman permainan.

Beberapa halaman juga menyediakan tombol **kembali** untuk kembali ke menu utama.

FiveGames juga memiliki fitur musik. Pemain dapat membuka pilihan musik dan memilih lagu yang tersedia dari playlist aplikasi.

---

# ♟️ Chess

Chess adalah permainan catur yang dimainkan pada papan 8 × 8.

### Cara Bermain

Pilih bidak yang ingin digerakkan, kemudian pilih kotak tujuan yang tersedia. Setelah pemain melakukan langkah, permainan akan melanjutkan giliran berikutnya secara otomatis.

Chess dapat dimainkan melawan bot maupun menggunakan mode permainan dua pemain apabila mode tersebut tersedia.

Tujuan permainan adalah mengalahkan lawan dengan strategi catur hingga mencapai kondisi **checkmate**.

### Setelah Permainan Selesai

Ketika permainan berakhir, pemain dapat memilih:

- **Lanjut** untuk memulai permainan baru.
- **Coba Lagi** untuk mengulang permainan.

---

# 🎯 Hangman

Hangman adalah permainan menebak kata berdasarkan jumlah huruf yang tersedia.

### Cara Bermain

Pemain akan mendapatkan sebuah kata yang masih disembunyikan. Pilih huruf yang tersedia untuk mencoba menebak kata tersebut.

Jika huruf yang dipilih terdapat dalam kata, posisi huruf tersebut akan terbuka. Jika salah, jumlah kesalahan akan bertambah.

Pemain harus menemukan kata sebelum batas kesalahan tercapai.

### Setelah Permainan Selesai

Setelah berhasil menebak kata atau permainan berakhir, pilih **Lanjut** atau **Coba Lagi** untuk memulai ronde baru dengan kata yang berbeda.

---

# 🧩 Maze

Maze adalah permainan mencari jalan keluar dari sebuah labirin.

### Cara Bermain

Gunakan tombol arah untuk menggerakkan pemain melalui labirin.

Kontrol utama:

**↑** untuk bergerak ke atas  
**↓** untuk bergerak ke bawah  
**←** untuk bergerak ke kiri  
**→** untuk bergerak ke kanan

Pemain harus mencari jalan menuju titik akhir tanpa melewati dinding labirin.

Tersedia juga tombol **Hint** berbentuk lampu. Hint dapat membantu menunjukkan jalur yang dapat digunakan dari posisi pemain menuju tujuan. Jalur tersebut hanya menjadi petunjuk dan tidak menggerakkan pemain secara otomatis.

### Setelah Permainan Selesai

Jika berhasil mencapai tujuan, pilih **Lanjut** untuk mendapatkan labirin berikutnya.

Jika permainan gagal, pilih **Coba Lagi** untuk membuat atau memulai kembali labirin.

---

# 💣 Minesweeper

Minesweeper adalah permainan mencari dan menghindari ranjau yang tersembunyi di dalam papan.

### Cara Bermain

Pemain harus membuka kotak-kotak pada papan dan berusaha menemukan area yang aman.

Setiap kotak dapat memberikan informasi yang membantu menentukan lokasi ranjau.

Jika pemain memilih kotak yang berisi ranjau, seluruh lokasi ranjau akan ditampilkan. Kotak ranjau akan ditandai dengan warna merah sebelum permainan berakhir.

### Setelah Permainan Selesai

Pilih **Coba Lagi** untuk langsung membuat papan baru dan memainkan ronde berikutnya.

---

# ❌⭕ Tic-Tac-Toe

Tic-Tac-Toe adalah permainan papan sederhana menggunakan simbol **X** dan **O**.

### Cara Bermain

Pemain bergantian memilih kotak kosong pada papan.

Tujuannya adalah membuat tiga simbol yang sama dalam satu garis, baik secara:

- horizontal,
- vertikal,
- maupun diagonal.

Pemain yang berhasil membuat tiga simbol dalam satu garis menjadi pemenang.

### Setelah Permainan Selesai

Pilih **Lanjut** atau **Coba Lagi** untuk memulai permainan berikutnya.

---

# 🎵 Musik

FiveGames menyediakan playlist musik yang dapat digunakan selama aplikasi berjalan.

Musik tersedia di dalam folder:

`assets/music`

Playlist dapat berisi beberapa pilihan lagu yang dapat dipilih melalui menu musik pada aplikasi.

---

# 🏠 Navigasi

Secara umum, alur penggunaan FiveGames adalah:

**Menu Utama → Pilih Game → Mainkan → Permainan Selesai → Lanjut / Coba Lagi**

Pemain dapat kembali ke menu utama apabila ingin mengganti permainan.

---

# 💾 Data Permainan

FiveGames menggunakan database SQLite untuk menyimpan data tertentu yang diperlukan oleh aplikasi.

Database aplikasi menggunakan file:

`sixgames.db`

File database merupakan bagian dari sistem aplikasi dan tidak perlu diubah secara manual oleh pemain.

---

# 📱 Menjalankan FiveGames

FiveGames dikembangkan menggunakan:

- **Python**
- **Flet**
- **Flutter**
- **SQLite**

Untuk menjalankan aplikasi dari source code, pastikan Python dan dependensi proyek telah tersedia.

Jalankan:

```bash
python main.py
