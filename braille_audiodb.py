# import sqlite3
# from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, OptionMenu
# from pathlib import Path
# import shutil
# import pygame

# DB_PATH = "braille_luganda.db"
# AUDIO_FOLDER = Path("audio_files")
# AUDIO_FOLDER.mkdir(exist_ok=True)

# # Initialize audio system
# pygame.mixer.init()

# def upload_audio():
#     selected_char = char_var.get()
#     if not selected_char:
#         messagebox.showwarning("No Character", "Please select a Luganda character.")
#         return

#     file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
#     if not file_path:
#         return

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     # Get braille_id for selected character
#     cursor.execute("SELECT id FROM braille_patterns WHERE luganda_char = ?", (selected_char,))
#     result = cursor.fetchone()
#     if not result:
#         conn.close()
#         messagebox.showerror("Error", f"No braille entry found for '{selected_char}'")
#         return
#     braille_id = result[0]

#     # Copy and rename file
#     dest_path = AUDIO_FOLDER / f"{selected_char}.mp3"
#     shutil.copy(file_path, dest_path)

#     # Insert or update audio mapping
#     cursor.execute("""
#         INSERT INTO audio_files (braille_id, audio_file_path)
#         VALUES (?, ?)
#         ON CONFLICT(braille_id) DO UPDATE SET audio_file_path=excluded.audio_file_path
#     """, (braille_id, str(dest_path)))

#     conn.commit()
#     conn.close()

#     messagebox.showinfo("Success", f"Audio file for '{selected_char}' uploaded successfully.")

# def play_audio():
#     selected_char = char_var.get()
#     if not selected_char:
#         messagebox.showwarning("No Character", "Please select a Luganda character.")
#         return

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT audio_file_path FROM audio_files a JOIN braille_patterns b ON a.braille_id = b.id WHERE b.luganda_char = ?", (selected_char,))
#     result = cursor.fetchone()
#     conn.close()

#     if not result:
#         messagebox.showerror("Error", f"No audio found for '{selected_char}'")
#         return

#     audio_path = result[0]

#     try:
#         pygame.mixer.music.load(audio_path)
#         pygame.mixer.music.play()
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to play audio: {e}")

# def load_characters():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT DISTINCT luganda_char FROM braille_patterns")
#     characters = sorted([row[0] for row in cursor.fetchall()])
#     conn.close()
#     return characters

# # GUI setup
# root = Tk()
# root.title("Braille Audio Uploader")
# root.geometry("400x250")

# Label(root, text="Select Luganda Character:").pack(pady=10)
# char_var = StringVar()
# char_list = load_characters()
# char_dropdown = OptionMenu(root, char_var, *char_list)
# char_dropdown.pack()

# Button(root, text="Upload Audio File", command=upload_audio).pack(pady=10)
# Button(root, text="Play Audio", command=play_audio).pack(pady=5)

# root.mainloop()
