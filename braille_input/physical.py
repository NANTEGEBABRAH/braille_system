from .base import BrailleInput

class PhysicalDeviceInput(BrailleInput):
    def listen(self, callback):
        raise NotImplementedError("Physical device support coming soon")