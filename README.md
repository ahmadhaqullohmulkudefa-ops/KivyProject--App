# 🎮 FiveGames

<p align="center">
  <b>Aplikasi kumpulan permainan sederhana berbasis Python dan Flet</b>
</p>

FiveGames adalah aplikasi kumpulan permainan yang menggabungkan beberapa game ke dalam satu aplikasi. Project ini dibuat menggunakan **Python** dengan framework **Flet** dan dikembangkan untuk dapat digunakan pada perangkat desktop maupun Android.

Aplikasi memiliki **5 permainan utama**, yaitu:

- ♟️ Chess
- 🔤 Hangman
- 🧩 Maze
- 💣 Minesweeper
- ❌⭕ Tic-Tac-Toe

Selain permainan, FiveGames juga memiliki **menu musik**, sistem **database**, navigasi antar halaman, serta sistem untuk memulai permainan baru setelah permainan selesai.

---

# 📋 Daftar Isi

- [Tentang Project](#-tentang-project)
- [Tujuan Project](#-tujuan-project)
- [Game yang Tersedia](#-game-yang-tersedia)
  - [Chess](#-1-chess)
  - [Hangman](#-2-hangman)
  - [Maze](#-3-maze)
  - [Minesweeper](#-4-minesweeper)
  - [Tic-Tac-Toe](#-5-tic-tac-toe)
- [Music](#-music)
- [Menu Utama](#-menu-utama)
- [Navigasi Aplikasi](#-navigasi-aplikasi)
- [Sistem Game Over](#-sistem-game-over)
- [Sistem Lanjut dan Coba Lagi](#-sistem-lanjut-dan-coba-lagi)
- [Database](#-database)
- [Teknologi](#-teknologi-yang-digunakan)
- [Struktur Project](#-struktur-project)
- [Penjelasan File](#-penjelasan-file)
- [Instalasi](#-instalasi)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Build APK](#-build-apk-android)
- [Git dan GitHub](#-git-dan-github)
- [Troubleshooting](#-troubleshooting)
- [Pengembangan](#-pengembangan-selanjutnya)
- [Developer](#-developer)
- [Status Project](#-status-project)

---

# 📌 Tentang Project

FiveGames dibuat sebagai sebuah aplikasi yang menyediakan beberapa permainan dalam satu tempat.

Konsep utama aplikasi adalah membuat pengguna dapat memilih permainan dari satu menu utama tanpa harus membuka aplikasi yang berbeda untuk setiap game.

Setiap game memiliki mekanisme permainan yang berbeda:

| Game | Jenis Permainan |
|---|---|
| ♟️ Chess | Strategi / Board Game |
| 🔤 Hangman | Tebak Kata |
| 🧩 Maze | Puzzle / Labirin |
| 💣 Minesweeper | Puzzle / Logika |
| ❌⭕ Tic-Tac-Toe | Board Game |

Aplikasi juga menyediakan fitur musik sebagai background music yang dapat dipilih oleh pengguna.

---

# 🎯 Tujuan Project

Project FiveGames dibuat untuk mempraktikkan kemampuan dalam:

- Pemrograman Python
- Pembuatan GUI
- Pengembangan aplikasi mobile
- Pengembangan game sederhana
- Pembuatan sistem navigasi
- Pengelolaan state permainan
- Event handling
- Penggunaan database SQLite
- Pengelolaan asset
- Penggunaan Git dan GitHub
- Build aplikasi Android menggunakan Flet

---

# 🎮 Game yang Tersedia

# ♟️ 1. Chess

Chess adalah permainan catur melawan bot.

Pemain bermain melawan komputer dan bot akan melakukan langkah secara otomatis setelah pemain melakukan langkah.

## ✨ Fitur Chess

- Papan catur interaktif
- Bidak catur
- Pemilihan bidak
- Pergerakan bidak
- Sistem pergantian giliran
- Pemain melawan bot
- Bot bergerak secara otomatis
- Pengecekan kondisi permainan
- Sistem game over
- Sistem permainan baru
- Reset papan ketika memulai permainan baru

## 🤖 Bot Chess

Pada Chess, pemain tidak perlu menekan tombol tambahan untuk meminta bot bergerak.

Setelah pemain melakukan langkah:

```text
Pemain bergerak
      ↓
Giliran berpindah
      ↓
Bot berpikir
      ↓
Bot bergerak otomatis
      ↓
Giliran pemain

Dengan sistem ini permainan dapat berlangsung secara otomatis antara pemain dan bot.
🕹️ Cara Bermain Chess
1. Buka menu utama.
2. Pilih Chess.
3. Pilih bidak yang ingin dimainkan.
4. Pilih posisi tujuan.
5. Setelah langkah dilakukan, bot akan bergerak secara otomatis.
6. Lanjutkan permainan sampai permainan berakhir.
7. Setelah game over, pemain dapat memulai permainan baru.
🔤 2. Hangman
Hangman adalah permainan menebak sebuah kata berdasarkan huruf.
Pemain harus memilih huruf untuk mencoba menemukan seluruh huruf yang terdapat pada kata.
✨ Fitur Hangman
- Kata rahasia
- Sistem tebakan huruf
- Daftar huruf yang sudah ditebak
- Sistem kesalahan
- Tampilan perkembangan kata
- Status permainan
- Kondisi menang
- Kondisi kalah
- Sistem ronde
- Tombol untuk memulai ronde baru
- Reset data permainan
🕹️ Cara Bermain Hangman
1. Pilih Hangman.
2. Kata akan ditampilkan dalam bentuk huruf yang belum lengkap.
3. Pilih huruf yang ingin ditebak.
4. Jika huruf benar, huruf akan ditampilkan pada posisi yang sesuai.
5. Jika huruf salah, jumlah kesalahan akan bertambah.
6. Tebak seluruh huruf untuk memenangkan permainan.
7. Jika kesempatan habis, permainan berakhir.
8. Gunakan tombol Lanjut atau Coba Lagi untuk memulai ronde baru.
🔄 Sistem Ronde
Setiap ronde memiliki kata baru.
Ketika ronde baru dimulai, sistem akan melakukan reset terhadap:
- Kata sebelumnya
- Huruf yang telah ditebak
- Jumlah kesalahan
- Status permainan
- Tampilan kata
🧩 3. Maze
Maze adalah permainan mencari jalan dari posisi awal menuju titik finish.
Pemain harus melewati labirin dengan menghindari dinding dan menemukan jalur menuju tujuan.
✨ Fitur Maze
- Labirin
- Posisi pemain
- Titik finish
- Sistem dinding
- Sistem pergerakan
- Kontrol arah
- Sistem pengecekan posisi
- Sistem kemenangan
- Sistem kegagalan
- Tombol Hint
- Sistem pencarian jalur
- Maze berikutnya
- Reset maze
🎮 Kontrol Maze
Kontrol utama berbentuk D-Pad:
        [ ↑ ]

    [ ← ][ ↓ ][ → ]

Fungsi tombol:
Tombol	Fungsi
↑	Bergerak ke atas
←	Bergerak ke kiri
↓	Bergerak ke bawah
→	Bergerak ke kanan


💡 Sistem Hint
Maze memiliki tombol Hint.
Hint digunakan untuk membantu pemain menemukan jalan menuju finish.
Sistem hint mencari jalur yang valid dari posisi pemain saat ini menuju tujuan dengan mempertimbangkan dinding pada maze.
Hint tidak menggerakkan pemain secara otomatis.
Pemain tetap harus mengikuti jalur tersebut menggunakan kontrol permainan.
🏆 Menyelesaikan Maze
Jika pemain berhasil mencapai titik finish:
Pemain mencapai finish
        ↓
Maze selesai
        ↓
Pemain dapat memilih Lanjut
        ↓
Maze berikutnya

🔄 Mengulang Maze
Jika permainan perlu diulang, pemain dapat menggunakan tombol Coba Lagi.
Maze akan dibuat/reset kembali sehingga pemain dapat mencoba lagi.
💣 4. Minesweeper
Minesweeper adalah permainan puzzle yang mengharuskan pemain membuka sel tanpa mengenai ranjau.
Pemain harus berhati-hati ketika memilih sel.
✨ Fitur Minesweeper
- Papan Minesweeper
- Sel permainan
- Sistem ranjau
- Pembukaan sel
- Pengecekan ranjau
- Kondisi game over
- Tampilan seluruh ranjau setelah terkena ranjau
- Warna merah untuk sel ranjau
- Sistem delay sebelum game over
- Tombol Coba Lagi
- Pembuatan papan baru
💣 Ketika Terkena Ranjau
Ketika pemain membuka sel yang berisi ranjau:
Ranjau terkena
      ↓
Seluruh ranjau ditampilkan
      ↓
Sel ranjau diberi warna merah
      ↓
Tunggu sebentar
      ↓
Game Over

🔄 Coba Lagi
Tombol Coba Lagi akan langsung:
- Menghapus kondisi game over
- Menghapus tampilan ranjau sebelumnya
- Membuat papan baru
- Menutup kembali seluruh sel
- Mengatur ulang status permainan
Pemain tidak perlu menekan tombol tambahan untuk melakukan reset.
🕹️ Cara Bermain Minesweeper
1. Pilih Minesweeper.
2. Pilih sel pada papan.
3. Perhatikan isi sel.
4. Hindari ranjau.
5. Lanjutkan membuka sel.
6. Jika terkena ranjau, semua ranjau akan ditampilkan.
7. Setelah game over, gunakan Coba Lagi untuk membuat permainan baru.

❌⭕ 5. Tic-Tac-Toe
Tic-Tac-Toe adalah permainan papan 3×3 menggunakan simbol X dan O.
Pemain bergantian mengisi kotak sampai salah satu pemain mendapatkan tiga simbol dalam satu garis atau seluruh papan terisi.
✨ Fitur Tic-Tac-Toe
- Papan 3×3
- Simbol X
- Simbol O
- Pergantian giliran
- Pengecekan kemenangan
- Pengecekan seri
- Kondisi game over
- Reset papan
- Permainan baru
🏆 Kondisi Menang
Pemain menang apabila mendapatkan tiga simbol yang sama dalam satu garis:
Horizontal
Vertical
Diagonal

Contoh:
X | X | X
---------
O | O | -
---------
- | - | -

🤝 Kondisi Seri
Jika seluruh kotak telah terisi dan tidak ada pemain yang mendapatkan tiga simbol dalam satu garis, permainan berakhir seri.
🕹️ Cara Bermain
1. Pilih Tic-Tac-Toe.
2. Pemain melakukan langkah.
3. Giliran berpindah.
4. Pemain berikutnya melakukan langkah.
5. Lanjutkan sampai terdapat pemenang atau hasil seri.
6. Gunakan tombol permainan baru untuk mengulang.
🎵 Music
FiveGames memiliki sistem musik yang digunakan untuk menyediakan background music.
File musik berada di:
assets/music/

🎵 Playlist
Playlist menggunakan file:
opsi1.mp3
opsi2.mp3
opsi3.mp3
opsi4.mp3
opsi5.mp3
opsi6.mp3
opsi7.mp3
opsi8.mp3

✨ Fitur Music
- Playlist musik
- Beberapa pilihan musik
- Musik sebagai background
- Pemilihan musik melalui menu
- Asset musik disimpan di dalam project
🏠 Menu Utama
Menu utama adalah halaman pertama ketika aplikasi dibuka.
Menu utama digunakan sebagai pusat navigasi menuju berbagai fitur aplikasi.
Menu yang Tersedia
                FiveGames
                    │
        ┌───────────┼───────────┐
        │           │           │
      Chess       Hangman      Maze
        │           │           │
        └───────────┼───────────┘
                    │
              Minesweeper
                    │
              Tic-Tac-Toe
                    │
                  Music

Pengguna dapat memilih game yang ingin dimainkan dari menu utama.
🔄 Navigasi Aplikasi
Alur penggunaan aplikasi secara umum:
Buka FiveGames
      ↓
  Menu Utama
      ↓
Pilih permainan
      ↓
  Mainkan game
      ↓
   Game selesai
      ↓
Lanjut / Coba Lagi
      ↓
Main kembali atau
kembali ke menu utama

Setiap game dapat dikembalikan ke menu utama melalui navigasi yang tersedia.
🔄 Sistem Lanjut dan Coba Lagi
FiveGames menggunakan sistem Lanjut dan Coba Lagi untuk memudahkan pemain memulai permainan kembali.
▶️ Lanjut
Digunakan untuk melanjutkan permainan atau level berikutnya pada game yang mendukung sistem tersebut.
Contohnya:
- Maze → lanjut ke maze berikutnya
- Hangman → memulai ronde berikutnya
- Game lain → memulai permainan baru sesuai sistem game
🔄 Coba Lagi
Digunakan untuk mengulang permainan dari awal.
Data permainan sebelumnya akan di-reset sesuai dengan jenis game.
Chess
- Papan di-reset
- Giliran di-reset
- Status permainan di-reset
Hangman
- Kata baru
- Huruf ditebak di-reset
- Kesalahan di-reset
- Status di-reset
Maze
- Maze baru/reset
- Posisi pemain kembali ke awal
- Status permainan di-reset
Minesweeper
- Papan baru
- Sel kembali tertutup
- Ranjau lama dihapus
- Status game over di-reset
Tic-Tac-Toe
- Papan dikosongkan
- Giliran di-reset
- Status kemenangan di-reset
💾 Database
FiveGames menggunakan database SQLite.
Database utama:
sixgames.db

Database digunakan sebagai bagian dari sistem penyimpanan data aplikasi.
⚠️ Catatan Database
File:
sixgames.db

merupakan database aplikasi.
Database tidak perlu diedit secara manual karena pengelolaan database dilakukan melalui program Python.
🛠️ Teknologi yang Digunakan
Teknologi	Fungsi
Python	Bahasa pemrograman utama
Flet	Framework GUI dan aplikasi
Flutter	Platform yang digunakan dalam proses build mobile
SQLite	Database
Android	Platform target mobile
Visual Studio Code	IDE / editor
Git	Version control
GitHub	Repository project


📂 Struktur Project
FiveGames/
│
├── main.py
├── common.py
│
├── chessgame.py
├── hangman.py
├── mazegame.py
├── minesweeper.py
├── tictactoe.py
│
├── database.py
├── sixgames.db
│
├── assets/
│   └── music/
│       ├── opsi1.mp3
│       ├── opsi2.mp3
│       ├── opsi3.mp3
│       ├── opsi4.mp3
│       ├── opsi5.mp3
│       ├── opsi6.mp3
│       ├── opsi7.mp3
│       └── opsi8.mp3
│
└── README.md

📄 Penjelasan File
main.py
File utama aplikasi.
Bertugas mengatur:
- Startup aplikasi
- Menu utama
- Navigasi
- Hubungan antar game
- Tampilan utama
- Sistem aplikasi secara keseluruhan
common.py
Berisi komponen atau fungsi yang dapat digunakan bersama oleh beberapa bagian aplikasi.
Tujuannya agar kode yang digunakan bersama tidak perlu ditulis berulang kali.
chessgame.py
Berisi seluruh sistem yang berhubungan dengan permainan Chess.
Meliputi:
- Papan
- Bidak
- Pergerakan
- Giliran
- Bot
- Status permainan
- Reset permainan
hangman.py
Berisi sistem permainan Hangman.
Meliputi:
- Kata
- Huruf
- Tebakan
- Kesalahan
- Status
- Ronde
- Reset permainan
mazegame.py
Berisi sistem permainan Maze.
Meliputi:
- Pembuatan maze
- Posisi pemain
- Dinding
- Finish
- Pergerakan
- Kontrol
- Hint
- Level
- Reset
minesweeper.py
Berisi sistem Minesweeper.
Meliputi:
- Pembuatan papan
- Ranjau
- Sel
- Pembukaan sel
- Game over
- Tampilan ranjau
- Reset
- Sistem delay game over
tictactoe.py
Berisi sistem permainan Tic-Tac-Toe.
Meliputi:
- Papan 3×3
- X
- O
- Giliran
- Pengecekan kemenangan
- Pengecekan seri
- Reset
database.py


