# app_files/handlers/Handler1.py

from .AbstractHandler import AbstractHandler

class Handler1(AbstractHandler):
    """Handler1 prints a message."""
    
    def process(self):
        print("Handler1 is processing!")
