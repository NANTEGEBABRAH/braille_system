from abc import ABC, abstractmethod

class BrailleInput(ABC):
    """Base class for all input methods"""
    @abstractmethod
    def listen(self, callback):
        """Start listening for input"""
        pass
    
    """to be implemented by abstract classes"""