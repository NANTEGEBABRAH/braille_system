from braille_processor import BrailleProcessor
from typing import List, Tuple
import re


class TranslationEngine:
    def __init__(self):
        self.processor = BrailleProcessor()
        self.braille_map = {
            # English letters
            (1,): 'a', (1,2): 'b', (1,4): 'c',
            (1,4,5): 'd', (1,5): 'e', (1,2,4): 'f',
            (1,2,4,5): 'g', (1,2,5): 'h', (2,4): 'i',
            (2,4,5): 'j', (1,3): 'k', (1,2,3): 'l',
            (1,3,4): 'm', (1,3,4,5): 'n', (1,3,5): 'o',
            (1,2,3,4): 'p', (1,2,3,4,5): 'q', (1,2,3,5): 'r',
            (2,3,4): 's', (2,3,4,5): 't', (1,3,6): 'u',
            (1,2,3,6): 'v', (2,4,5,6): 'w', (1,3,4,6): 'x',
            (1,3,4,5,6): 'y', (1,3,5,6): 'z',
            
            # Luganda special characters
            (1,4,6): 'ny', (1,2,4,6): 'ng',
            (1,5,6): 'gw', (2,4,6): 'ky',
            (1,2,5,6): 'ly'
        }

    def _get_phonetic(self, char: str) -> str:
        """Get IPA phonetic representation"""
        phonetics = {
            # Vowels
        'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
        
        # Consonants
        'b': 'b', 'c': 'tʃ', 'd': 'd', 'f': 'f', 'g': 'ɡ',
        'h': 'h', 'j': 'dʒ', 'k': 'k', 'l': 'l', 'm': 'm',
        'n': 'n', 'p': 'p', 'r': 'r', 's': 's', 't': 't',
        'v': 'v', 'w': 'w', 'y': 'j', 'z': 'z',
        
        # Luganda digraphs
        'ny': 'ɲ', 'ng': 'ŋ', 'gw': 'ɡʷ',
        'ky': 'c', 'ly': 'ʎ', 'mp': 'mp',
        'nt': 'nt', 'nk': 'ŋk', 'gy': 'ɟ',
            'i' : 'yi',
        
        # Special cases
        'ng\'': 'ŋ',  # For words like ng'ombe
        'n\'': 'ŋ',   # Alternate nasal representation
        '?': '?'      # Unknown character
    }
        return phonetics.get(char.lower(), char)
        
    def translate(self, dots: list) -> tuple:
        """Convert Braille dots to Luganda text"""
        dot_tuple = tuple(sorted(dots))
        luganda = self.braille_map.get(dot_tuple, 'Not available')
        return [luganda], [self._get_phonetic(luganda)]
    
    
    def get_word_details(self, braille_word: str) -> dict:
        """Get detailed information about a Braille word"""
        # Check if it's a known common word
        cursor = self.processor.conn.cursor()
        
        cursor.execute (
            ''' SELECT * FROM common_words WHERE braille_pattern = ?''',
            (braille_word,)
        )
        word_info = cursor.fetchone()
        
        if word_info:
            return dict(word_info)
        
        # If not a common word, return character-by-character analysis
        analysis = {
            'braille_pattern': braille_word,
            'luganda_word': self.processor.translate_braille_word(braille_word),
            'character_breakdown': []
        }
        
        for char in braille_word:
            mapping = self.processor.get_braille_mapping(char)
            if mapping:
                analysis['character_breakdown'].append(dict(mapping))
            else:
                analysis['character_breakdown'].append({
                    'braille_code': char,
                    'luganda_char': '?',
                    'description': 'Unknown character'
                })
        
        return analysis
    
    def close(self):
        self.processor.close()

if __name__ == "__main__":
    engine = TranslationEngine()
    
    # Test translation
    braille_text = '''⠁⠃⠁⠃ ⠁⠃⠁⠝⠞⠑⠑ ⠙ ⠑'''
    luganda, phonetic = engine.translate(braille_text)
    print("Luganda:", luganda)
    print("Phonetic:", phonetic)
    
    # Test word analysis
    print(engine.get_word_details('⠁⠃⠁⠃⠑'))
    print(engine.get_word_details('⠑⠙⠑⠑'))
    
    engine.close()