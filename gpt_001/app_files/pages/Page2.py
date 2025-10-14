# app_files/pages/Page2.py

# from .AbstractPage import AbstractPage
import tkinter as tk
from app_files.pages.AbstractPage import AbstractPage

from app_files.handlers.Handler2 import Handler2

class Page2(AbstractPage):
    """Page 2 of the application, using Handler2."""
    
    def __init__(self, parent, controller):
        self.handler = Handler2()
        super().__init__(parent, controller)


    def load_widgets(self):

        self.page2_label = tk.Label(self, text="This is Page 2!")
        self.page2_label.pack(pady=20)

        self.page2_btn_run_handler = tk.Button(self, text="Run Handler2", command=self.run_handler)
        self.page2_btn_run_handler.pack(pady=20)

        self.page2_btn_home = tk.Button(self, text="Back to Home", 
                                    command=lambda: self.controller.show_page("HomePage"))
        self.page2_btn_home.pack(pady=20)



    def reset_defaults(self):
        pass

    def run_handler(self):
        self.handler.process()
