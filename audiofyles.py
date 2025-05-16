# import sqlite3
# import os
# from pathlib import Path

# def setup_audio_files():
#     db_path = Path("braille_luganda.db")
#     if not db_path.exists():
#         print("Database not found. Please run the main database setup first.")
#         return
    
#     conn = sqlite3.connect("db_path")
#     cursor = conn.cursor()
    
#     conn.execute("PRAGMA foreign_keys = ON")
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS audio_files (
#         aud_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         braille_id INTEGER UNIQUE NOT NULL,
#         audio_file_path TEXT NOT NULL,
#         FOREIGN KEY (braille_id) REFERENCES braille_patterns(id)
#     )
#     """)
    
    
#     # Insert standard letters a-z
#     inserted = 0
#     for char in "abcdefghijklmnopqrstuvwxyz":
#         cursor.execute("SELECT id FROM braille_patterns WHERE luganda_char = ?", (char,))
#         result = cursor.fetchone()
        
#         if result:
#             braille_id = result[0]
#             audio_file_path = f"audio_files/{char}.mp3"
#             # Check if already inserted to prevent duplicates
#             cursor.execute("SELECT * FROM audio_files WHERE braille_id = ?", (braille_id,))
#             if cursor.fetchone() is None:
#                 cursor.execute("""
#                 INSERT INTO audio_files (braille_id, audio_file_path)
#                 VALUES (?, ?)
#                 """, (braille_id, audio_file_path))
#                 inserted += 1
        
#         conn.commit()
#         conn.close()

#         print(f"Audio files table created/updated. {inserted} records inserted.")
        
#     if __name__ == "__main__":
#         setup_audio_files()
        
