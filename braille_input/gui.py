from .base import BrailleInput
import tkinter as tk
from typing import List, Set, Optional, Callable
import queue
import threading

class GUIInput(BrailleInput):
    def __init__(self, master=None):
        super().__init__()
        self.current_dots = set()
        self.dot_buttons = []
        self.callback = None
        self._showing = False
        self._gui_thread = None
        self._event_queue = queue.Queue()
        self.key_map = {'f':1, 'd':2, 's':3, 'j':4, 'k':5, 'l':6}
        
        # Initialize root window in main thread only
        if threading.current_thread() is threading.main_thread():
            self.root = tk.Tk() if master is None else tk.Toplevel(master)
            self.root.withdraw()
        else:
            self.root = None
        self._gui_ready = threading.Event()

    def listen(self, callback):
        """Thread-safe window initialization"""
        self.callback = callback
    
        if threading.current_thread() is threading.main_thread():
            self._create_window()
        else:
            # Signal main thread to create window
            self._event_queue.put(("create_window", None))
            self._gui_ready.wait()  # Wait for GUI to be ready

    def _create_window(self):
        """Create the actual visible window with guaranteed visibility"""
        self.root = tk.Tk()
        if not self.root:
            return  # Prevent creation if root doesn't exist
        self.root.withdraw()  # Hide until fully initialized
        self._setup_gui_components()
        self._finalize_window()

    def _setup_gui_components(self):
        """Set up all GUI components using named colors"""
        self.root.title("Virtual Braille Keyboard")
        self.root.geometry("500x300")
        self.root.configure(bg='light gray')  # Using named color
        
        # Main container
        main_frame = tk.Frame(self.root, bg='light gray', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Current Dots: None",
            font=("Arial", 14, "bold"),
            bg='light gray',
            fg='black'
        )
        self.status_label.pack(pady=10)

        # Dot buttons frame
        dot_frame = tk.Frame(main_frame, bg='light gray')
        dot_frame.pack()
        
        # Create buttons in proper Braille pattern (2x3 grid)
        positions = [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]
        for dot, (row, col) in zip(range(1,7), positions):
            btn = tk.Button(
                dot_frame,
                text=f"Dot {dot}",
                command=lambda d=dot: self._handle_dot_press(d),
                width=6,
                height=2,
                relief=tk.RAISED,
                bg='white',
                fg='black',
                activebackground='light blue'
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.dot_buttons.append(btn)

        # Submit button
        submit_btn = tk.Button(
            main_frame,
            text="SUBMIT (Space)",
            command=self._submit_dots,
            height=1,
            width=15,
            bg='light green',
            fg='black',
            activebackground='green'
        )
        submit_btn.pack(pady=10)

    def _finalize_window(self):
        """Complete window setup and display"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        # Key bindings
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        
        # Window display and focus
        self.root.deiconify()
        self._showing = True
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()
        
        # Start update loop
        self._start_update_loop()
        self.root.mainloop()

    def _start_update_loop(self):
        """Start the GUI update loop"""
        if not hasattr(self, 'root') or not self._showing or not self.root:
            return
    
        try:
            self._update_display()
            # Store the after ID so we can cancel it later
            self._update_loop_id = self.root.after(100, self._start_update_loop)
        except (tk.TclError, AttributeError):
            # Window was destroyed - stop the loop
            self._showing = False
            self._update_loop_id = None

    def _handle_dot_press(self, dot: int) -> None:
        """Handle physical or virtual dot button presses."""
        if dot in self.current_dots:
            self.current_dots.remove(dot)
            self.dot_buttons[dot-1].config(relief=tk.RAISED, bg='white')
        else:
            self.current_dots.add(dot)
            self.dot_buttons[dot-1].config(relief=tk.SUNKEN, bg='lightgray')
        self._update_display()

    def _on_key_press(self, event: tk.Event) -> None:
        """Handle keyboard key presses (f, d, s, j, k, l → dots 1-6)."""
        if event.keysym.lower() in self.key_map:
            dot = self.key_map[event.keysym.lower()]
            if dot not in self.current_dots:
                self.current_dots.add(dot)
                self.dot_buttons[dot-1].config(relief=tk.SUNKEN, bg='lightgray')
                self._update_display()
        elif event.keysym == 'space':
            self._submit_dots()

    def _on_key_release(self, event: tk.Event) -> None:
        """Handle keyboard key releases."""
        if event.keysym.lower() in self.key_map:
            dot = self.key_map[event.keysym.lower()]
            if dot in self.current_dots:
                self.current_dots.remove(dot)
                self.dot_buttons[dot-1].config(relief=tk.RAISED, bg='white')
                self._update_display()

    def _submit_dots(self) -> None:
        """Submit the current Braille character."""
        if self.callback and self.current_dots:
            self.callback(sorted(self.current_dots))
            self._clear_visual_dots()
            self.current_dots.clear()
            self._update_display()

    def _clear_visual_dots(self) -> None:
        """Reset all dot buttons to their default state."""
        for btn in self.dot_buttons:
            btn.config(relief=tk.RAISED, bg='white')

    def _update_display(self) -> None:
        """Update the status label with currently pressed dots."""
        if self.status_label:
            dots_text = sorted(self.current_dots) if self.current_dots else "None"
            self.status_label.config(text=f"Current Dots: {dots_text}")

    def get_current_input(self) -> List[int]:
        """Return currently selected dots as a sorted list."""
        return sorted(self.current_dots.copy())
    
    def _on_close(self):
        """Handle window closing properly"""
        self._showing = False
        if hasattr(self, '_update_loop_id') and self._update_loop_id:
            try:
                self.root.after_cancel(self._update_loop_id)
            except tk.TclError:
                pass
        if self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def stop(self) -> None:
        self._showing = False
        
        if hasattr(self, '_update_loop_id'):
            try:
                self.root.after_cancel(self._update_loop_id)
            except (tk.TclError, AttributeError):
                pass
        
        # Destroy window safely
        if hasattr(self, 'root') and self.root:
            try:
                if threading.current_thread() is threading.main_thread():
                    self.root.destroy()
                else:
                    self.root.after(0, self.root.destroy)
            except tk.Tclerror:
                pass
            
        #Cleanup state
        self.current_dots.clear()
        self.callback = None