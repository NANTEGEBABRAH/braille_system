import sqlite3
from typing import List, Optional, Dict

class BrailleProcessor:
    def __init__(self, db_path: str = 'braille_luganda.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        
    def get_braille_mapping(self, braille_code: str) -> Optional[Dict]:
        """Get Luganda mapping for a single Braille character"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM braille_patterns WHERE braille_code = ?',
            (braille_code,)
        )
        return cursor.fetchone()
    
    def translate_braille_word(self, braille_word: str) -> Optional[str]:
        """Translate a Braille word to Luganda"""
        # First try exact match in common words
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT luganda_word FROM common_words WHERE braille_pattern = ?',
            (braille_word,)
        )
        result = cursor.fetchone()
        
        if result:
            return result['luganda_word']
        
        # If not found, translate character by character
        translated_chars = []
        for char in braille_word:
            mapping = self.get_braille_mapping(char)
            if mapping:
                translated_chars.append(mapping['luganda_char'])
            else:
                translated_chars.append('?')  # Unknown character
        
        return ''.join(translated_chars)
    
    def process_braille_input(self, input_text: str) -> List[str]:
        """Process multi-line Braille input"""
        lines = input_text.split('\n')
        translated_lines = []
        
        for line in lines:
            # Split into words (Braille words are separated by space)
            braille_words = line.split(' ')
            translated_words = []
            
            for word in braille_words:
                translated_word = self.translate_braille_word(word)
                if translated_word:
                    translated_words.append(translated_word)
            
            translated_lines.append(' '.join(translated_words))
        
        return translated_lines
    
    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    processor = BrailleProcessor()
    
    # Test single character
    print(processor.get_braille_mapping('⠁'))  # Should return 'a'
    print(processor.get_braille_mapping('⠃'))  # Should return 'b'
    
    # Test word translation
    print(processor.translate_braille_word('⠁⠃⠁⠃⠊'))  # Should return 'ababi'
    
    # Test multi-line processing
    test_input = '''⠁⠃⠁⠃⠊ ⠃⠁⠝⠛⠊'''
    print(processor.process_braille_input(test_input))
    
    processor.close()