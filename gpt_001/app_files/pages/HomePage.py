# app_files/pages/HomePage.py
import tkinter as tk
from app_files.pages.AbstractPage import AbstractPage

class HomePage(AbstractPage):

    def __init__(self, parent, controller):
        self.is_homepage = True
        super().__init__(parent, controller)

    def load_widgets(self):
        self.home_label = tk.Label(self, text="This is the HomePage!")
        self.home_label.pack(pady=20)

        self.home_button1 = tk.Button(self, text="Go to Page 1", command=lambda: self.controller.show_page("Page1"))
        self.home_button1.pack(pady=20)

        self.home_button2 = tk.Button(self, text="Go to Page 2", command=lambda: self.controller.show_page("Page2"))
        self.home_button2.pack(pady=20)

    def reset_defaults(self):
        pass

