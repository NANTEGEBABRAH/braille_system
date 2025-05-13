from main_app import BrailleToLugandaApp
from gtts import gTTS
import cmd
import os

class BrailleCLI(cmd.Cmd):
    prompt = '(braille-luganda) '
    
    def __init__(self):
        super().__init__()
        self.app = BrailleToLugandaApp()
        print("Braille to Luganda Translator")
        print("Type 'help' for commands\n")
    
    def do_translate(self, arg):
        """Translate Braille text: translate <braille_text>"""
        if not arg:
            print("Please provide Braille text to translate")
            return
        
        luganda, phonetic = self.app.process_input(arg)
        print("\nTranslation Results:")
        print("Luganda:", ' | '.join(luganda))
        print("Phonetic:", ' | '.join(phonetic))
    
    def do_speak(self, arg):
        """Speak the translation: speak [line_number]"""
        line_index = 0
        if arg:
            try:
                line_index = int(arg)
            except ValueError:
                print("Please provide a valid line number")
                return
        
        if not self.app.speak_translation(line_index):
            print("No translation available or invalid line number")
    
    def do_analyze(self, arg):
        """Analyze a Braille word: analyze <braille_word>"""
        if not arg:
            print("Please provide a Braille word to analyze")
            return
        
        analysis = self.app.get_word_analysis(arg)
        print("\nWord Analysis:")
        for key, value in analysis.items():
            if key == 'character_breakdown':
                print(f"{key}:")
                for char in value:
                    print(f"  - {char['braille_code']}: {char['luganda_char']} ({char.get('description', '')})")
            else:
                print(f"{key}: {value}")
    
    def do_export(self, arg):
        """Export translation: export <filename> [json|text]"""
        args = arg.split()
        if len(args) < 1:
            print("Please provide a filename")
            return
        
        filename = args[0]
        format = 'json' if len(args) < 2 else args[1]
        
        if format not in ['json', 'text']:
            print("Invalid format. Use 'json' or 'text'")
            return
        
        if self.app.export_translation(filename, format):
            print(f"Translation exported to {filename} ({format})")
        else:
            print("Export failed. No translation available or file error")
    
    def do_quit(self, arg):
        """Exit the application"""
        self.app.close()
        print("Goodbye!")
        return True
    
    def do_clear(self, arg):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    BrailleCLI().cmdloop()