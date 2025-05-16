from pathlib import Path
import pygame
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
import tempfile
from io import BytesIO
import os
import time
from typing import Optional, List, Dict
from gtts import gTTS

class AudioSystem:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.audio_cache: Dict[str, str] = {}
        # Only directly playable formats now
        self.supported_formats = ['.wav', '.mp3', '.ogg']
        self.special_combinations = {
            'ny': ['n', 'y'],
            'nny': ['n', 'ny'],
            'nng': ['n', 'ng'],
            # Add other Luganda-specific combinations
        }
        
        # Create directories if needed
        self.cache_dir = Path('audio_cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.local_audio_dir = Path('audio_files')
        self.local_audio_dir.mkdir(exist_ok=True)
        self.dot_descriptions = {
            1: "dot 1",
            2: "dot 2",
            3: "dot 3",
            4: "dot 4",
            5: "dot 5",
            6: "dot 6"
        }
        self._current_sound = None  # To hold the sound object
        
    def play_dot_sound(self, dot: int):
        """Generate and play TTS for a single dot"""
        if not hasattr(self, 'dot_descriptions'):
            self.dot_descriptions = {i: f"dot {i}" for i in range(1,7)}
            
        if dot not in range(1, 7):
            return
            
        try:
            # Generate TTS audio on-the-fly
            tts = gTTS(text=self.dot_descriptions[dot], lang='en', slow=False, lang_check=False)
            
            # Create in-memory file
            with BytesIO() as fp:
                tts.write_to_fp(fp)
                fp.seek(0)
            
                # Load and play sound
                if pygame.mixer.get_init():  # Check if mixer is initialized
                    if self._current_sound:  # Stop any currently playing sound
                        self._current_sound.stop()
                        
                # Play the audio
                sound = pygame.mixer.Sound(fp)
                sound.play()
            
                # Keep reference to prevent garbage collection
                self._current_sound = sound
            
        except Exception as e:
            print(f"Error generating dot sound: {e}")
            # Fallback to system beep
            try:
                beep = pygame.mixer.Sound(buffer=bytearray([127]*100))
                beep.play()
            except Exception as beep_error:
                print(f"Beep fallback failed: {beep_error}")
    
    def play_luganda_audio(self, word: str, volume_boost: float =2.0) -> bool:
        for ext in ['.wav', '.mp3', '.ogg']:
            audio_file = self.local_files_dir / f"{word.lower()}{ext}"
            if audio_file.exists():
                try:
                    sound = pygame.mixer.Sound(audio_file)
                    
                    #sound.set_volume(min(volume_boost, 3.0))
                    sound_array = pygame.sndarray.array(sound)
                    boosted = np.clip(sound_array * volume_boost, -32768, 32767)
                    sound = pygame.sndarray.make_sound(boosted.astype(np.int16))
                    sound.play()
                    return True
                except Exception as e:
                    print(f"Audio play error: {e}")
                    # Fallback attempt with standard volume
                    try:
                        sound = pygame.mixer.Sound(audio_file)
                        sound.play()
                        return True
                    except:
                        continue
        return False

    def _find_audio_file(self, base_name: str) -> Optional[Path]:
        """Find audio files in supported formats"""
        for ext in self.supported_formats:
            file_path = self.local_audio_dir / f"{base_name}{ext}"
            if file_path.exists():
                return file_path
        return None

    def _play_local_audio(self, text: str) -> bool:
        """Handle Luganda audio playback with multi-character support"""
        text = text.lower().strip()
        if not text:
            return False

        # Process special cases first
        for combo, parts in self.special_combinations.items():
            text = text.replace(combo, ''.join(parts))

        # Split into playable segments
        segments = self._split_to_audio_segments(text)
        if not segments:
            return False

        # Play all segments with small pauses
        for segment in segments:
            audio_file = self._find_audio_file(segment)
            if not audio_file or not self._play_single_file(audio_file):
                return False
            time.sleep(0.05)  # Small pause between sounds
        return True

    def _split_to_audio_segments(self, text: str) -> List[str]:
        """Convert text to playable audio segments"""
        text = text.lower().strip()
        segments = []
        
        # First try the full word
        if self._find_audio_file(text):
            return [text]
        
        # Then try special combinations
        for combo, parts in self.special_combinations.items():
            if combo in text:
                # Try to split around the special combination
                parts_before = self._split_to_audio_segments(text[:text.index(combo)])
                parts_after = self._split_to_audio_segments(text[text.index(combo)+len(combo):])
                if parts_before and parts_after:
                    return parts_before + parts + parts_after
        
        # Fallback to character by character analysis
        i = 0
        while i < len(text):
            found = False
            # Check for longest matches first (3, 2, then 1 chars)
            for length in [3, 2, 1]:
                if i + length > len(text):
                    continue
                segment = text[i:i+length]
                if self._find_audio_file(segment):
                    segments.append(segment)
                    i += length
                    found = True
                    break
            if not found:
                i += 1  # Skip unknown characters
        return segments

    def _play_single_file(self, filepath: Path) -> bool:
        """Play a single audio file"""
        if not filepath.exists():
            return False
            
        try:
            sound = pygame.mixer.Sound(str(filepath))
            channel = sound.play()
            
            # Wait for playback to finish
            while channel and channel.get_busy():
                time.sleep(0.05)
            return True
        except Exception as e:
            print(f"Error playing {filepath}: {e}")
            return False

    def text_to_speech(self, text: str, lang: str = 'lg') -> Optional[str]:
        """Convert text to speech using gTTS with caching"""
        if not text.strip():
            return None

        cache_key = f"{lang}_{text}"
        if cache_key in self.audio_cache:
            return self.audio_cache[cache_key]

        try:
            filename = f"tts_{abs(hash(text))}.mp3"
            filepath = self.cache_dir / filename
            
            if not filepath.exists():
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(str(filepath))
            
            self.audio_cache[cache_key] = str(filepath)
            return str(filepath)
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
        
    def play_translation(self, text: str, lang: str = 'lg') -> bool:
        """Play audio for translated text"""
        if not text.strip():
            return False
            
        # Try pre-recorded audio first
        audio_file = self.local_audio_dir / f"{text.lower()}.mp3"
        if audio_file.exists():
            return self._play_audio_file(audio_file)
        
        # Fallback to system TTS (you'll need gTTS installed)
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang, slow=False)
            temp_file = self.local_audio_dir / "temp_tts.mp3"
            tts.save(temp_file)
            return self._play_audio_file(temp_file)
        except ImportError:
            print("gTTS not available for TTS fallback")
            return False

    def _play_audio_file(self, filepath: Path) -> bool:
        """Play a single audio file"""
        try:
            sound = pygame.mixer.Sound(str(filepath))
            sound.play()
            return True
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
        
    def speak(self, text: str, lang: str = 'lg') -> bool:
        """Main method to speak text with fallback support"""
        # First try local audio files in any supported format
        if lang == 'lg' and self._play_local_audio(text):
            return True
            
        # Fallback to TTS
        tts_file = self.text_to_speech(text, lang)
        if tts_file:
            return self._play_single_file(Path(tts_file))
        return False

    def clear_cache(self):
        """Clear all cached audio files"""
        for filepath in self.audio_cache.values():
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing {filepath}: {e}")
                
        self.audio_cache = {}
        print("Audio cache cleared")
        
    

if __name__ == "__main__":
    audio = AudioSystem()
    
    # Test cases
    tests = [
        ("n", 'lg'),  # looks for n.wav/mp3/ogg
        ("test", 'en'),     #English test, uses text-to-speech
        ("nyonyi", 'lg'),  #look for nyonyi.wav/mp3/ogg
        ("mukwano", 'lg'),  #look for mukwano.wav/mp3/ogg
    ]
    
    for text, lang in tests:
        print(f"\nAttempting to play '{text}' in {lang}:")
        print("Searching for audio files...")
        
        # Debug file search
        base_text = text.lower()
        for ext in audio.supported_formats:
            test_file = audio.local_audio_dir / f"{base_text}{ext}"
            if test_file.exists():
                print(f"Found source file: {test_file}")
        
        success = audio.speak(text, lang)
        print("✓ Success!" if success else "✗ Failed")
        time.sleep(1)
    
    audio.clear_cache()