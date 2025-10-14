import tkinter as tk
from app_files.handlers.number_handler import NumberHandler
from .AbstractPage import AbstractPage


class Page2(AbstractPage):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, controller)

        self.label = tk.Label(self, text="Random Number", font=('Helvetica', 16))
        self.randomize_button = tk.Button(self, text="Randomize Number", command=self.randomize_number)
        self.back_button = tk.Button(self, text="Back", command=lambda: self.controller.show_page('HomePage'))

    def load_widgets(self):
        self.label.pack(pady=10)
        self.page1_button.pack(pady=10)
        self.page2_button.pack(pady=10)


    def randomize_number(self):
        random_number = NumberHandler.randomize_number()
        self.label.config(text=f"Selected Number: {random_number}")

    def reset_defaults(self):
        pass