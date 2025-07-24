# GrowBot GUI (Growtopia AutoFarm Recorder)

Aplikasi GUI Python modern untuk merekam dan menjalankan aksi mouse/keyboard otomatis (auto farm bot Growtopia) dengan tampilan dark mode berbasis CustomTkinter.

## ✨ Fitur Utama
- **Rekam Posisi Mouse**: Pickup, Place, dan banyak Break point dengan klik mouse.
- **Simpan/Load Record**: Kelola banyak rekaman aksi ke/dari file JSON.
- **Dropdown Record Selector**: Pilih dan load record dengan dropdown yang selalu update.
- **Normalisasi Koordinat**: Posisi mouse otomatis disesuaikan dengan resolusi layar.
- **AutoFarm Bot**: Jalankan bot dengan pengaturan hit count, delay, dan loop count.
- **STOP Global**: Tekan tombol SPACE di mana saja untuk menghentikan bot.
- **UI Modern**: 100% CustomTkinter, dark mode, responsif, dan user-friendly.
- **Minimize Otomatis**: Jendela minimize otomatis saat bot berjalan.

## 📦 Cara Install & Jalankan
1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install customtkinter pyautogui pynput
   ```
3. **Jalankan aplikasi:**
   ```bash
   python growbot_gui.py
   ```

## 🖱️ Cara Pakai
1. Tekan **Set Pickup** lalu klik posisi pickup di layar Growtopia.
2. Tekan **Set Place** lalu klik posisi place.
3. Tekan **+ Break** lalu klik posisi break (bisa lebih dari satu).
4. Atur **Hit Count**, **Delay**, dan **Loop Count** sesuai kebutuhan.
5. Tekan **Simpan Rekaman** untuk menyimpan record.
6. Pilih record di dropdown untuk load/mengedit.
7. Tekan **Mulai AutoFarm** untuk menjalankan bot (window akan minimize otomatis).
8. Tekan **SPACE** di keyboard untuk menghentikan bot kapan saja.
9. Tekan **Clear Rekaman** untuk menghapus semua record.

## 📁 File Data
- `_recordings.json` : Menyimpan semua record.
- `_current_record.json` : Menyimpan record yang sedang aktif.

## 📝 Catatan
- Masih dalam developing
- Pastikan resolusi layar tidak berubah drastis antara merekam dan menjalankan bot.
- Jika mouse tidak bisa direkam, coba jalankan aplikasi sebagai administrator.
- UI sudah full CustomTkinter, tidak ada sisa Tkinter.