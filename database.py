import sqlite3
from pathlib import Path

def create_database():
    """Initialize the SQLite database with required tables"""
    db_path = Path('braille_luganda.db')
    
    if db_path.exists():
        # Remove existing database if needed
        db_path.unlink()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Braille patterns table
    cursor.execute('''
        CREATE TABLE braille_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        braille_code TEXT UNIQUE NOT NULL,
        luganda_char TEXT NOT NULL,
        ipa_pronunciation TEXT,
        description TEXT
        )
    ''')
    
    # Create words table
    cursor.execute('''
    CREATE TABLE common_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        braille_pattern TEXT NOT NULL,
        luganda_word TEXT NOT NULL,
        english_meaning TEXT,
        category TEXT
    )
    ''')
    
# Create user settings table
    cursor.execute('''
    CREATE TABLE user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT UNIQUE NOT NULL,
        setting_value TEXT NOT NULL
    )
    ''')
    
    
    # Some of the basic Luganda Braille mappings (6-dot Braille)
    basic_mappings = [
        ('⠁', 'a', 'a', 'Luganda vowel a'),
        ('⠃', 'b', 'b', 'Luganda consonant b'),
        ('⠉', 'c', 'tʃ', 'Luganda consonant c (ch sound)'),
        ('⠙', 'd', 'd', 'Luganda consonant d'),
        ('⠑', 'e', 'e', 'Luganda vowel e'),
        ('⠋', 'f', 'f', 'Luganda consonant f'),
        ('⠛', 'g', 'g', 'Luganda consonant g'),
        ('⠓', 'h', 'h', 'Luganda consonant h'),
        ('⠊', 'i', 'i', 'Luganda vowel i'),
        ('⠚', 'j', 'dʒ', 'Luganda consonant j (j sound)'),
        ('⠅', 'k', 'k', 'Luganda consonant k'),
        ('⠇', 'l', 'l', 'Luganda consonant l'),
        ('⠍', 'm', 'm', 'Luganda consonant m'),
        ('⠝', 'n', 'n', 'Luganda consonant n'),
        ('⠕', 'o', 'o', 'Luganda vowel o'),
        ('⠏', 'p', 'p', 'Luganda consonant p'),
        ('⠟', 'q', '', 'Luganda consonant q (not used)'),
        ('⠗', 'r', 'r', 'Luganda consonant r'),
        ('⠎', 's', 's', 'Luganda consonant s'),
        ('⠞', 't', 't', 'Luganda consonant t'),
        ('⠥', 'u', 'u', 'Luganda vowel u'),
        ('⠧', 'v', 'v', 'Luganda consonant v'),
        ('⠭', 'w', 'w', 'Luganda consonant w'),
        ('⠽', 'x', '', 'Luganda consonant x (not used)'),
        ('⠾', 'y', 'y', 'Luganda consonant y'),
        ('⠵', 'z', 'z', 'Luganda consonant z'),
    ]
    
    cursor.executemany(
        'INSERT INTO braille_patterns (braille_code, luganda_char, ipa_pronunciation, description) VALUES (?, ?, ?, ?)',
        basic_mappings
    )
    
    
    #some common words
    common_words = [
        ('⠁⠃⠁⠃⠊', 'ababi', 'bad people', 'nouns'),
        ('⠁⠃⠁⠝⠞⠥', 'abantu', 'people', 'nouns'),
        ('⠍⠥⠅⠭⠁⠝⠕', 'mukwano', 'friend', 'noun')
    ]
    
    cursor.executemany(
        'INSERT INTO common_words (braille_pattern, luganda_word, english_meaning, category) VALUES (?, ?, ?, ?)',
        common_words
    )
    
    # Set default user settings
    default_settings = [
        ('speech_speed', 'normal'),
        ('voice_gender', 'female'),
        ('audio_volume', '100'),
    ]
    
    cursor.executemany(
        'INSERT INTO user_settings (setting_name, setting_value) VALUES (?, ?)',
        default_settings
    )
    
    conn.commit()
    conn.close()
    print("Database setup completed successfully.")

if __name__ == "__main__":
    create_database()
    
