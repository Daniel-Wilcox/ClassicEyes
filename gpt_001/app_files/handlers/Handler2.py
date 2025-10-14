# app_files/handlers/Handler2.py

from .AbstractHandler import AbstractHandler

class Handler2(AbstractHandler):
    """Handler2 prints a message."""
    
    def process(self):
        print("Handler2 is processing!")
