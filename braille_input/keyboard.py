from pynput.keyboard import Listener, Key
import time
import pygame
from .base import BrailleInput

class KeyboardInput(BrailleInput):
    def __init__(self):
        self.current_dots = set()  # Preserves multi-key presses
        self.callback = None
        self.last_key_time = time.time()
        self.dot_map = {
            'f': 1, 'd': 2, 's': 3,
            'j': 4, 'k': 5, 'l': 6
        }
        self.listener = None
        

    def listen(self, callback):
        """Non-blocking listener that preserves chorded input"""
        self.callback = callback
        self.listener = Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=True
        )
        self.listener.start()

    def _on_press(self, key):
        """Handles multiple simultaneous key presses"""
        try:
            char = key.char.lower()
            if char in self.dot_map:
                self.current_dots.add(self.dot_map[char])  # Add to current combination
                self.last_key_time = time.time()
                print(f"Current dots: {self.current_dots}")  # Debug multi-key input

        except AttributeError:
            if key == Key.space:
                self._submit_dots()

    def _on_release(self, key):
        """Clears only the released key"""
        try:
            char = key.char.lower()
            if char in self.dot_map:
                dot = self.dot_map[char]
                if dot in self.current_dots:
                    self.current_dots.remove(dot)
        except AttributeError:
            pass

    def _submit_dots(self):
        """Preserves full multi-character submissions"""
        if self.current_dots:
            self.callback(sorted(self.current_dots))  # Sends complete combination
            self.current_dots.clear()

    def update(self):
        """Auto-submit check integrated with main loop"""
        if self.awaiting_submit and (time.time() - self.last_key_time >= 0.3):
            self._submit_dots()

    def stop(self):
        if self.listener:
            self.listener.stop()
            
    def get_current_input(self) -> list:
        """Returns currently pressed dots as sorted list"""
        return sorted(self.current_dots.copy())