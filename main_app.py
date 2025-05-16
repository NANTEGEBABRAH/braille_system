from translation_engine import TranslationEngine
from audio_system import AudioSystem
from typing import List, Tuple, Optional, Union
import json
import argparse
import sys
import time
from io import BytesIO
import base64
import pygame
import threading
import tkinter as tk
from gtts import gTTS
from braille_input.gui import GUIInput
from braille_input.physical import PhysicalDeviceInput
from braille_input.keyboard import KeyboardInput

COLORS = {
    'background': (240, 240, 250), # Light lavender
    'title': (30, 30, 120), # Dark blue
    'input': (200, 50, 50), # Red
    'translation': (50, 150, 50), # Green
    'instructions': (80, 80, 80), # Dark gray
    'braille_cell': (180, 180, 255) # Light blue
}

class BrailleToLugandaApp:
    def __init__(self, input_method: str = "keyboard"):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        #set display mode immediately
        self.screen = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Braille to Luganda Translator")
        
        #initialize mixer
        try:
            pygame.mixer.init()
        except:
            print("Audio mixer initialization failed")
        
        #rest of initialization
        self._initialize_components(input_method)
        
        # Force initial render
        self._update_display()
        pygame.display.flip()
    def _initialize_components(self, input_method):
            
        self.audio = AudioSystem()
        self.braille_cell_pos = (500, 100)
        self.current_dots = set()
        self.display_text = ""

        # Fonts with multiple fallbacks
        self.font = self._get_font(32)
        self.small_font = self._get_font(24)
        self.translation_font = self._get_font(28)
    
        # Core components
        self.engine = TranslationEngine()
        self.current_translation = None
        
        # Initialize TTS status
        self.tts_available = True
        self.active_tts = None  # Will hold current TTS playback
        
        # Input handler setup
        self.input_methods = {
            "keyboard": KeyboardInput(),
            "gui": GUIInput(),
            "physical": PhysicalDeviceInput()
        }
        self.input_handler = self._setup_input_method(input_method)
        
        # State tracking
        self.current_input = []
        self.last_translation = ""
        self.running = True
        self.is_playing = False
    
        # Start input listening
        self._start_input_listening()
        
        print("Window initialized successfully")
        
    def _get_font(self, size):
        """Robust font loading with fallbacks"""
        fonts = ['Arial', 'Liberation Sans', 'DejaVu Sans', None]
        for font in fonts:
            try:
                return pygame.font.SysFont(font, size) if font else pygame.font.Font(None, size)
            except:
                continue
        return pygame.font.Font(None, size)
    
    def _start_input_listening(self):
        """Start listening for input based on selected method"""
        if isinstance(self.input_handler, GUIInput):
            # GUI needs special thread handling
            if threading.current_thread() is threading.main_thread():
                self.input_handler.listen(self._process_braille_input)
            else:
                threading.Thread(
                    target=self.input_handler.listen,
                    args=(self._process_braille_input,),
                    daemon=True
                ).start()
        else:
            self.input_handler.listen(self._process_braille_input)
    
    def _update_display(self):
        """Safely update the display with error handling"""
        try:
            self.screen.fill(COLORS['background'])
            
            # Title
            title = self.font.render("Braille to Luganda Translator", True, COLORS['title'])
            self.screen.blit(title, (20, 20))
            
            # Braille cell visualization
            pygame.draw.rect(self.screen, COLORS['braille_cell'], (*self.braille_cell_pos, 200, 300))
            
            # Draw dots
            active_dots = self._normalize_dots(self.current_input)
            
            for dot in range(1, 7):
                pos = self._get_dot_position(dot)
                color = (0, 0, 0) if dot in active_dots else (200, 200, 200)
                pygame.draw.circle(self.screen, color, pos, 15)
                
                # Show dot numbers
                if dot in active_dots:
                    num_text = self.small_font.render(str(dot), True, (255,255,255))
                    self.screen.blit(num_text, (pos[0]-5, pos[1]-8))
                
            # Current input
            input_text = self.small_font.render(f"Pressed: {active_dots}", True, COLORS['input'])
            self.screen.blit(input_text, (20, 80))
            
            # Translation
            trans_rect = pygame.Rect(20, 120, 400, 60)
            pygame.draw.rect(self.screen, (255,255,255), trans_rect, 2)
            if self.last_translation:
                trans_text = self.font.render(f"Translation: {self.last_translation}", True, COLORS['translation'])
                self.screen.blit(trans_text, (30, 130))
            
            # Instructions
            instructions = [
                "Instructions:",
                "Press Dot 1 to 6 on virtual keyboard",
                "F(1)/D(2)/S(3)/J(4)/K(5)/L(6): are mapped respectively",
                "Space: Used to submit"
            ]
                
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, COLORS['instructions'])
                self.screen.blit(text, (20, 200 + i * 30))
            
            pygame.display.flip()
        except Exception as e:
            print(f"Display error: {e}")
            
    def _get_dot_position(self, dot: int) -> Tuple[int, int]:
        """Calculate positions for Braille cell dots"""
        x, y = self.braille_cell_pos
        column_spacing = 60
        row_spacing = 60
        padding = 40
    
        positions = {
            1: (x + padding, y + padding),
            2: (x + padding, y + padding + row_spacing),
            3: (x + padding, y + padding + 2*row_spacing),
            4: (x + padding + column_spacing, y + padding),
            5: (x + padding + column_spacing, y + padding + row_spacing),
            6: (x + padding + column_spacing, y + padding + 2*row_spacing)
        }
        return positions.get(dot, (0, 0))

    def _normalize_dots(self, dots: Union[str, List[int], None]) -> List[int]:
        """Safely convert dots to standard list format"""
        if not dots:
            return []
        if isinstance(dots, str):
            try:
                clean_str = dots.strip('[]')
                return [int(d) for d in clean_str.split(',') if d.strip().isdigit()]
            except ValueError:
                return []
        return [int(d) for d in dots]

    def start_listening(self):
        """Main application loop"""
        clock = pygame.time.Clock()
        while self.running:
        
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                
                self._update_display()
                pygame.display.flip()
                clock.tick(60)
                
            except pygame.error as e:
                print(f"pygame error:{e}")
                self.running = False
        
    def _setup_input_method(self, method: str):
        """Initialize the selected input method"""
        try:
            return self.input_methods[method]
        except KeyError:
            print(f"Invalid input method '{method}'. Defaulting to keyboard.")
            return self.input_methods["keyboard"]

    def _process_braille_input(self, dots):
        """Handle incoming Braille dots"""
        if not dots:
            return
        
        try:
            self.current_input = dots
            
            # 1. Play dot confirmation sounds
            self._play_dot_sound(dots)
            
            # Get translation after dots finish
            luganda, _ = self.engine.translate(dots)
            if luganda:
                self.display_text = luganda[0]
                self.last_translation = self.display_text
                
                # 3. Delay translation audio by the remaining dot sound duration
                translation_delay = self._calculate_remaining_dot_duration(dots)
                threading.Timer(translation_delay,
                        lambda: self.audio.play_translation(self.display_text, 'lg')).start()
            else:
                self.display_text = ""
                self.last_translation = "No translation found"
                
            self._update_display()
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            self.last_translation = "Translation error"
            self._update_display()
            
    def _calculate_remaining_dot_duration(self, dots: List[int]) -> float:
        
        base_duration_per_dot = 0.20 * len(dots)
        inter_dot_buffer = 0.10
        total_duration = (base_duration_per_dot * len(dots)) + inter_dot_buffer
        
        return min(max(total_duration, 0.5), 1.5)  # Cap at 1 second max delay
            
    def _play_dot_sound(self, dots: List[int]):
        """Play TTS announcements for dot presses while maintaining fallbacks"""
        try:
            # 1. First stop any existing dot sounds
            pygame.mixer.stop()  # Stop all sounds except music
            
            # Create faster TTS for all dots at once
            dot_text = " ".join(f"dot {dot}" for dot in sorted(dots))
            tts = gTTS(text=dot_text, lang='en', slow=False)
        
            # Play through pygame mixer Use in-memory audio with faster playback
            with BytesIO() as fp:
                tts.write_to_fp(fp)
                fp.seek(0)
                
                # Load and modify playback speed
                sound = pygame.mixer.Sound(fp)
                sound.set_volume(0.6)
                
                # Play with shorter delay
                channel = sound.play()
                if channel:
                    # Fade out quickly if translation starts
                    channel.set_endevent(pygame.USEREVENT)
            
            # Short delay to prevent audio cutoff
            pygame.time.delay(300)  # 150ms delay
            
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            # Fallback to individual dot sounds or beeps
            try:
                for dot in dots:
                    try:
                        sound = pygame.mixer.Sound(f"audio/dot_{dot}.wav")
                        sound.play()
                        time.sleep(0.05)
                    except:
                        # Final fallback to system beep
                        beep = pygame.mixer.Sound(buffer=bytearray([80] * 30))
                        beep.play()
                        time.sleep(0.05)
            except Exception as fallback_error:
                print(f"Fallback audio error: {fallback_error}")
            
    def close(self):
        """Clean up resources safely"""
        
        if hasattr(self, 'input_handler'):
            self.input_handler.stop()
            
        # Then pygame
        if pygame.get_init():
            pygame.init
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Braille to Luganda Translator')
    parser.add_argument('--input', choices=['keyboard', 'gui', 'physical'],
                        default='keyboard', help='Input method')
    args = parser.parse_args()

    app = None
    try:
        # Initialize app with error handling
        try:
            app = BrailleToLugandaApp(input_method=args.input)
        except pygame.error as e:
            print(f"Failed to initialize Pygame: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Application initialization failed: {e}")
            sys.exit(1)

        # Main execution with proper event handling
        app.start_listening()

    except KeyboardInterrupt:
        print("\nUser interrupted the application")
    except pygame.error as e:
        print(f"Pygame runtime error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Guaranteed cleanup with error protection
        if app is not None:
            try:
                app.close()
            except Exception as e:
                print(f"Error during cleanup: {e}")
        
        # Ensure complete pygame shutdown
        if pygame.get_init():
            try:
                pygame.quit()
            except:
                pass
        
        print("Application shutdown complete")