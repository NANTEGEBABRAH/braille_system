import sqlite3
from pathlib import Path

def setup_luganda_characters():
    conn = sqlite3.connect("braille_luganda.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS luganda_characters (
        char_id INTEGER PRIMARY KEY AUTOINCREMENT,
        luganda_char TEXT UNIQUE NOT NULL,
        braille_pattern TEXT NOT NULL
        audio_file_path TEXT NOT NULL,
        FOREIGN KEY (braille_pattern) REFERENCES braille_patterns(braille_pattern)
    )
    """)
    #GET ALL BRAILLE_PATTERNS FROM THE BRAILLE_PATTERN TABLE FROM A TO Z
    cursor.execute("SELECT luganda_char, braille_pattern FROM braille_patterns WHERE luganda_char IN ('a','b','c',...)")
    braille_mappings = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Insert standard letters a-z
    for i, char in enumerate("abcdefghijklmnopqrstuvwxyz", start=1):
        braille_pattern = braille_mappings.get(char, "?")  # Fallback to "?" if not found
        audio_file_path = f"audio_files/{char}.mp3"
        cursor.execute(
            """INSERT INTO luganda_characters
        (luganda_char, braille_pattern, audio_file_path)
        VALUES (?, ?, ?)""",
            (char, braille_pattern, audio_file_path)
        )
    if __name__ == "__main__":
        setup_luganda_characters()