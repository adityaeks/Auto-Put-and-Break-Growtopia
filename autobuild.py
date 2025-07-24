import os
import time
from datetime import datetime
from watchfiles import watch
import subprocess
import psutil

WATCH_DIR = '.'
BUILD_TARGET = 'growbot_gui.py'
EXE_NAME = 'dist/growbot_gui.exe'
EXE_PROCESS_NAME = 'growbot_gui.exe'
LOG_FILE = 'build.log'

def log_change(message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{now}] {message}\n")
    print(f"[{now}] {message}")

def is_file_locked(path):
    try:
        with open(path, 'a'):
            return False
    except PermissionError:
        return True
    except FileNotFoundError:
        return False

def kill_running_exe():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == EXE_PROCESS_NAME:
            try:
                proc.kill()
                log_change(f"🔪 Proses {EXE_PROCESS_NAME} berhasil dihentikan (PID {proc.info['pid']})")
            except Exception as e:
                log_change(f"❌ Gagal menghentikan proses {EXE_PROCESS_NAME}: {e}")

def build_exe():
    if is_file_locked(EXE_NAME):
        log_change(f"⛔ File {EXE_NAME} sedang digunakan. Coba hentikan prosesnya dulu.")
        return

    log_change(f"⚙️ Memulai build: {BUILD_TARGET}")
    try:
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--noconfirm',
            '--windowed',
            BUILD_TARGET
        ], check=True)
        log_change(f"✅ Build selesai: {EXE_NAME}")
    except subprocess.CalledProcessError as e:
        log_change(f"❌ Build gagal: {e}")

if __name__ == '__main__':
    log_change(f"[WATCHER] Memulai pemantauan folder: {WATCH_DIR}")
    for changes in watch(WATCH_DIR):
        for change_type, changed_file in changes:
            if changed_file.endswith('.py'):
                log_change(f"🔍 Perubahan terdeteksi: {changed_file}")
                kill_running_exe()
                build_exe()
