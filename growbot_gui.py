import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
from pynput import mouse
import sys
import os
import json
from pyautogui import size as get_screen_size



# --- GUI START ---
root = tk.Tk()
root.title("🌱 Growtopia AutoFarm Recorder")
root.geometry("1000x1000")
root.update_idletasks()
root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
root.resizable(False, False)
root.configure(bg="#23272f")

# Style helpers
LABEL_FONT = ("Segoe UI", 11, "bold")
ENTRY_FONT = ("Segoe UI", 11)
BTN_FONT = ("Segoe UI", 10, "bold")
BTN_COLOR = {"bg": "#3b4252", "fg": "#e5e9f0", "activebackground": "#5e81ac", "activeforeground": "#eceff4"}
HIGHLIGHT = {"bg": "#2e3440", "fg": "#a3be8c"}


recordings_file = "_recordings.json"
if os.path.exists(recordings_file):
    with open(recordings_file, "r") as f:
        recordings = json.load(f)
else:
    recordings = []

loop_count = tk.IntVar(value=3)

# Load current_record from file if exists
if os.path.exists("_current_record.json"):
    with open("_current_record.json", "r") as f:
        current_record = json.load(f)
        if current_record.get('pickup'):
            current_record['pickup'] = tuple(current_record['pickup'])
        if current_record.get('place'):
            current_record['place'] = tuple(current_record['place'])
        if current_record.get('break_coords'):
            current_record['break_coords'] = [tuple(coord) for coord in current_record['break_coords']]
else:
    current_record = {
        'pickup': None,
        'place': None,
        'break_coords': [],
        'hit': 3,
        'delay': 0.2,
        'screen_size': get_screen_size()
    }
running = False


def get_mouse_position(label):
    def update_pos():
        x, y = pyautogui.position()
        label.config(text=f"{x}, {y}")
        label.after(100, update_pos)
    update_pos()




def set_position(type_, label):
    # Tutup window utama
    root.destroy()
    # Baca current_record dari file jika ada
    if os.path.exists("_current_record.json"):
        with open("_current_record.json", "r") as f:
            cr = json.load(f)
    else:
        cr = {
            'pickup': None,
            'place': None,
            'break_coords': [],
            'hit': 3,
            'delay': 0.2,
            'screen_size': get_screen_size()
        }
    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            cr[type_] = [x, y]
            cr['screen_size'] = get_screen_size()
            with open("_current_record.json", "w") as f:
                json.dump(cr, f)
            listener.stop()
    # Listener mouse
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Restart aplikasi
    python = sys.executable
    os.execl(python, python, *sys.argv)


def add_break_point(listbox):
    # Tutup window utama
    root.destroy()
    # Baca current_record dari file jika ada
    if os.path.exists("_current_record.json"):
        with open("_current_record.json", "r") as f:
            cr = json.load(f)
            if cr.get('break_coords'):
                cr['break_coords'] = [tuple(coord) for coord in cr['break_coords']]
    else:
        cr = {
            'pickup': None,
            'place': None,
            'break_coords': [],
            'hit': 3,
            'delay': 0.2,
            'screen_size': get_screen_size()
        }
    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            if 'break_coords' not in cr or cr['break_coords'] is None:
                cr['break_coords'] = []
            cr['break_coords'].append([x, y])
            cr['screen_size'] = get_screen_size()
            with open("_current_record.json", "w") as f:
                json.dump(cr, f)
            listener.stop()
    from pynput import mouse
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    python = sys.executable
    os.execl(python, python, *sys.argv)


def refresh_record_dropdown():
    record_names = [f"Record {i+1}" for i in range(len(recordings))]
    menu = record_dropdown['menu']
    menu.delete(0, 'end')
    for name in record_names:
        menu.add_command(label=name, command=lambda value=name: selected_record.set(value))
    if record_names:
        selected_record.set(record_names[-1])
    else:
        selected_record.set("")


def save_record():
    if not current_record['pickup'] or not current_record['place'] or not current_record['break_coords']:
        messagebox.showerror("Error", "Lengkapi pickup, place, dan break terlebih dahulu!")
        return
    # Simpan rekaman ke recordings dan file
    recordings.append(current_record.copy())
    with open(recordings_file, "w") as f:
        json.dump(recordings, f)
    messagebox.showinfo("Info", f"Rekaman ke-{len(recordings)} disimpan!")
    refresh_record_dropdown()
    reset_current()


def reset_current():
    current_record['pickup'] = None
    current_record['place'] = None
    current_record['break_coords'] = []
    with open("_current_record.json", "w") as f:
        json.dump(current_record, f)
    listbox_breaks.delete(0, tk.END)
    label_pickup.config(text="-")
    label_place.config(text="-")


def run_bot():

    global running
    running = True
    try:
        loops = loop_count.get()
    except:
        messagebox.showerror("Error", "Loop harus angka")
        return

    # Minimize window saat mulai auto farm
    root.iconify()

    def execute(record):
        # Normalisasi pickup, place, break_coords
        screen_now = get_screen_size()
        rec_screen = tuple(record.get('screen_size', screen_now))
        pickup = normalize_point(record['pickup'], rec_screen, screen_now)
        place = normalize_point(record['place'], rec_screen, screen_now)
        pyautogui.click(*pickup)
        time.sleep(0.2)
        pyautogui.click(*place, button='right')
        time.sleep(0.3)
        for coord in record['break_coords']:
            norm_coord = normalize_point(coord, rec_screen, screen_now)
            for _ in range(record['hit']):
                pyautogui.click(*norm_coord)
                time.sleep(record['delay'])

    def loop_all():
        # Jalankan hanya record yang dipilih di dropdown
        if selected_record.get().startswith("Record"):
            idx = int(selected_record.get().split()[1]) - 1
            if 0 <= idx < len(recordings):
                for i in range(loops):
                    if not running:
                        break
                    execute(recordings[idx])
                    time.sleep(0.5) 
        messagebox.showinfo("Done", "Loop selesai!")

    threading.Thread(target=loop_all).start()
def clear_recordings():
    global recordings
    if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus semua rekaman?"):
        recordings = []
        # Hapus isi file _recordings.json juga
        with open(recordings_file, "w") as f:
            json.dump(recordings, f)
        reset_current()
        refresh_record_dropdown()
        messagebox.showinfo("Info", "Semua rekaman telah dihapus.")
def stop_bot():
    global running
    running = False




# --- GUI LAYOUT ---

label_pickup = tk.Label(root, text="-", font=LABEL_FONT, **HIGHLIGHT, bd=1, relief="solid", padx=8, pady=2)
label_place = tk.Label(root, text="-", font=LABEL_FONT, **HIGHLIGHT, bd=1, relief="solid", padx=8, pady=2)
listbox_breaks = tk.Listbox(root, height=5, font=ENTRY_FONT, bg="#2e3440", fg="#eceff4", selectbackground="#5e81ac", selectforeground="#eceff4", bd=1, relief="solid")

btn_set_pickup = tk.Button(root, text="Set Pickup", font=BTN_FONT, **BTN_COLOR, command=lambda: set_position('pickup', label_pickup))
btn_set_place = tk.Button(root, text="Set Place", font=BTN_FONT, **BTN_COLOR, command=lambda: set_position('place', label_place))
btn_add_break = tk.Button(root, text="+ Break", font=BTN_FONT, **BTN_COLOR, command=lambda: add_break_point(listbox_breaks))

btn_save = tk.Button(root, text="💾 Simpan Rekaman", font=BTN_FONT, bg="#5e81ac", fg="#eceff4", activebackground="#81a1c1", activeforeground="#eceff4", command=save_record)
btn_start = tk.Button(root, text="▶ Mulai AutoFarm", font=BTN_FONT, bg="#a3be8c", fg="#23272f", activebackground="#b5e0a8", activeforeground="#23272f", command=run_bot)
btn_stop = tk.Button(root, text="⛔ STOP", font=BTN_FONT, bg="#bf616a", fg="#eceff4", activebackground="#d08770", activeforeground="#23272f", command=stop_bot)
btn_clear = tk.Button(root, text="🗑️ Clear Rekaman", font=BTN_FONT, bg="#ebcb8b", fg="#23272f", activebackground="#e5e9f0", activeforeground="#23272f", command=clear_recordings)

spin_hit = tk.Spinbox(root, from_=1, to=10, width=5, font=ENTRY_FONT, bg="#eceff4", fg="#23272f", command=lambda: current_record.update({'hit': int(spin_hit.get())}))
spin_delay = tk.Spinbox(root, from_=0.1, to=2.0, increment=0.1, width=5, font=ENTRY_FONT, bg="#eceff4", fg="#23272f", command=lambda: current_record.update({'delay': float(spin_delay.get())}))
spin_loop = tk.Spinbox(root, from_=1, to=999, textvariable=loop_count, width=5, font=ENTRY_FONT, bg="#eceff4", fg="#23272f")


# --- Modernized Layout ---
row = 0
tk.Label(root, text="Pickup Posisi:", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=0, sticky="w", padx=8, pady=8)
label_pickup.grid(row=row, column=1, sticky="w", padx=8, pady=8)
btn_set_pickup.grid(row=row, column=2, padx=8, pady=8)
row += 1

tk.Label(root, text="Place Posisi:", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=0, sticky="w", padx=8, pady=8)
label_place.grid(row=row, column=1, sticky="w", padx=8, pady=8)
btn_set_place.grid(row=row, column=2, padx=8, pady=8)
row += 1

tk.Label(root, text="Break Coords:", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=0, sticky="nw", padx=8, pady=8)
listbox_breaks.grid(row=row, column=1, sticky="w", padx=8, pady=8)
btn_add_break.grid(row=row, column=2, padx=8, pady=8)
btn_clear.grid(row=row, column=3, padx=8, pady=8)
row += 1

tk.Label(root, text="Hit Count:", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=0, sticky="w", padx=8, pady=8)
spin_hit.grid(row=row, column=1, sticky="w", padx=8, pady=8)
tk.Label(root, text="Delay (sec):", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=2, sticky="w", padx=8, pady=8)
spin_delay.grid(row=row, column=3, sticky="w", padx=8, pady=8)
row += 1

btn_save.grid(row=row, column=0, padx=8, pady=16)
btn_start.grid(row=row, column=1, padx=8, pady=16)
btn_stop.grid(row=row, column=2, padx=8, pady=16)
row += 1

tk.Label(root, text="Loop Count:", font=LABEL_FONT, bg="#23272f", fg="#e5e9f0").grid(row=row, column=0, sticky="w", padx=8, pady=8)
spin_loop.grid(row=row, column=1, sticky="w", padx=8, pady=8)

# Update label pickup/place dari file JSON setelah label dibuat
if os.path.exists("_current_record.json"):
    with open("_current_record.json", "r") as f:
        cr = json.load(f)
        if cr.get('pickup'):
            label_pickup.config(text=f"{cr['pickup'][0]}, {cr['pickup'][1]}")
        if cr.get('place'):
            label_place.config(text=f"{cr['place'][0]}, {cr['place'][1]}")
        # Tambahkan break_coords ke listbox_breaks
        if cr.get('break_coords'):
            for coord in cr['break_coords']:
                listbox_breaks.insert(tk.END, f"{coord[0]}, {coord[1]}")

# Dropdown untuk memilih record yang tersimpan
selected_record = tk.StringVar()

# --- Custom Dropdown (OptionMenu) Styling ---
from tkinter import ttk
style = ttk.Style()
style.theme_use('clam')
style.configure('TMenubutton', font=ENTRY_FONT, background="#2e3440", foreground="#eceff4", borderwidth=1, relief="solid")
style.map('TMenubutton', background=[('active', '#5e81ac')], foreground=[('active', '#eceff4')])

record_names = [f"Record {i+1}" for i in range(len(recordings))]
if record_names:
    selected_record.set(record_names[0])
else:
    selected_record.set("")

record_dropdown = ttk.OptionMenu(root, selected_record, selected_record.get(), *record_names)
record_dropdown.config(width=30)
record_dropdown.grid(row=row, column=0, columnspan=2, padx=8, pady=12, sticky="we")
row += 1

# Fungsi untuk load record ke current_record dan update GUI
def load_record(idx):
    if 0 <= idx < len(recordings):
        rec = recordings[idx]
        current_record.clear()
        current_record.update(rec)
        # Konversi pickup, place, break_coords ke tuple
        if current_record.get('pickup'):
            current_record['pickup'] = tuple(current_record['pickup'])
        if current_record.get('place'):
            current_record['place'] = tuple(current_record['place'])
        if current_record.get('break_coords'):
            current_record['break_coords'] = [tuple(coord) for coord in current_record['break_coords']]
        # Update file current_record.json
        with open("_current_record.json", "w") as f:
            json.dump(current_record, f)
        # Update label dan listbox
        if current_record.get('pickup'):
            label_pickup.config(text=f"{current_record['pickup'][0]}, {current_record['pickup'][1]}")
        else:
            label_pickup.config(text="-")
        if current_record.get('place'):
            label_place.config(text=f"{current_record['place'][0]}, {current_record['place'][1]}")
        else:
            label_place.config(text="-")
        listbox_breaks.delete(0, tk.END)
        if current_record.get('break_coords'):
            for coord in current_record['break_coords']:
                listbox_breaks.insert(tk.END, f"{coord[0]}, {coord[1]}")
        # Update spinbox hit dan delay sesuai record
        if 'hit' in current_record:
            spin_hit.delete(0, tk.END)
            spin_hit.insert(0, str(current_record['hit']))
        if 'delay' in current_record:
            spin_delay.delete(0, tk.END)
            spin_delay.insert(0, str(current_record['delay']))

# Callback untuk dropdown
def on_select_record(*args):
    if selected_record.get().startswith("Record"):
        idx = int(selected_record.get().split()[1]) - 1
        load_record(idx)

selected_record.trace_add('write', on_select_record)

# Start posisi tracker
get_mouse_position(tk.Label(root))


# --- Normalisasi koordinat saat klik ---
def normalize_point(point, from_size, to_size):
    x, y = point
    fx, fy = from_size
    tx, ty = to_size
    nx = int(x * tx / fx)
    ny = int(y * ty / fy)
    return (nx, ny)


# Perbaiki: stop_bot() harus bisa menghentikan thread loop_all
def on_space_press(event):
    stop_bot()
    # Jangan tampilkan messagebox di thread utama saat loop berjalan, cukup update judul window
    root.title("Growtopia AutoFarm Recorder [STOPPED by SPACE]")

root.bind_all('<Key-space>', on_space_press)

root.mainloop()
 