# app_files/handlers/AbstractHandler.py

class AbstractHandler:
    """Base class for all handlers."""
    
    def process(self):
        """Override this to implement specific processing functionality."""
        raise NotImplementedError("Subclasses should implement this!")
