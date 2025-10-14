# app_files/pages/Page1.py

# from .AbstractPage import AbstractPage
import tkinter as tk
from app_files.pages.AbstractPage import AbstractPage

from app_files.handlers.Handler1 import Handler1

class Page1(AbstractPage):
    """Page 1 of the application, using Handler1."""
    
    def __init__(self, parent, controller):
        self.handler = Handler1()        
        super().__init__(parent, controller)



    def load_widgets(self):

        self.page1_label = tk.Label(self, text="This is Page 1!")
        self.page1_label.pack(pady=20)

        self.page1_btn_run_handler = tk.Button(self, text="Run Handler1", command=self.run_handler)
        self.page1_btn_run_handler.pack(pady=20)

        self.page1_btn_home = tk.Button(self, text="Back to Home", 
                             command=lambda: self.controller.show_page("HomePage"))
        self.page1_btn_home.pack(pady=20)



    def reset_defaults(self):
        pass

    def run_handler(self):
        self.handler.process()

