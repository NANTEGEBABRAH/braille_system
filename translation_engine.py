from braille_processor import BrailleProcessor
from typing import List, Tuple
import re
from pathlib import Path


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
        
    def translate(self, input_data) -> tuple:
        """Handle both string and list inputs"""
        if isinstance(input_data, str):
            return self._translate_text(input_data)
        elif isinstance(input_data, list):
            return self._translate_dots(input_data)
        else:
            raise ValueError("Input must be string or list of dots")

    def _translate_text(self, braille_text: str) -> tuple:
        """Convert Braille text string to Luganda"""
        luganda_words = []
        phonetic_words = []
        
        for braille_word in braille_text.split(' '):
            luganda_chars = []
            phonetic_chars = []
            
            for braille_char in self._split_braille_chars(braille_word):
                dots = self._get_dots_from_braille_char(braille_char)
                if dots:
                    dot_tuple = tuple(sorted(dots))
                    luganda = self.braille_map.get(dot_tuple, '?')
                    luganda_chars.append(luganda)
                    phonetic_chars.append(self._get_phonetic(luganda))
            
            luganda_words.append(''.join(luganda_chars))
            phonetic_words.append(''.join(phonetic_chars))
        
        return ' '.join(luganda_words), ' '.join(phonetic_words)

    def _translate_dots(self, dots_list: list) -> tuple:
        """Convert list of dots to Luganda"""
        dot_tuple = tuple(sorted(dots_list))
        luganda = self.braille_map.get(dot_tuple, '?')
        return [luganda], [self._get_phonetic(luganda)]
    
    def _split_braille_chars(self, braille_word: str) -> list:
        """Split a Braille word into individual characters"""
        #Braille characters are Unicode characters in the range U+2800 to U+28FF
        return [c for c in braille_word if '\u2800' <= c <= '\u28FF']

    def _get_dots_from_braille_char(self, braille_char: str) -> list:
        """Convert a Braille Unicode character to its dot pattern"""
        # The Unicode Braille pattern is determined by the bits representing dots
        # Each dot position corresponds to a bit in the Unicode value
        code = ord(braille_char) - 0x2800
        dots = []
    
        # Braille dot numbering:
        # 1 4
        # 2 5
        # 3 6
        # 7 8 (though standard Braille only uses 1-6)
    
        if code & 0x01: dots.append(1)  # Dot 1
        if code & 0x02: dots.append(2)  # Dot 2
        if code & 0x04: dots.append(3)  # Dot 3
        if code & 0x08: dots.append(4)  # Dot 4
        if code & 0x10: dots.append(5)  # Dot 5
        if code & 0x20: dots.append(6)  # Dot 6
    
        return dots
    
    
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
    braille_text = """⠁⠃⠁⠝⠞⠥ ⠁⠃⠁⠃⠑ ⠃⠁⠙⠙⠁"""
    luganda, phonetic = engine.translate(braille_text)
    print("Luganda:", luganda)
    print("Phonetic:", phonetic)
    
    # Test word analysis
    print(engine.get_word_details('⠁⠃⠁⠃⠑'))
    print(engine.get_word_details('⠑⠙⠙⠊'))
    
    engine.close()