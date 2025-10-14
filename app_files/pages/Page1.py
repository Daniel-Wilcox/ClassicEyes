import tkinter as tk

from app_files.handlers.color_handler import ColorHandler  
import AbstractPage
# from pages import AbstractPage

class Page1(AbstractPage):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, controller)

        self.label = tk.Label(self, text="Random Color", font=('Helvetica', 16))
        self.randomize_button = tk.Button(self, text="Randomize Color", command=self.randomize_color)
        self.back_button = tk.Button(self, text="Back", command=lambda: self.controller.show_page('HomePage'))
    

    def load_widgets(self):
        self.label.pack(pady=10)
        self.page1_button.pack(pady=10)
        self.page2_button.pack(pady=10)

    def randomize_color(self):
        random_color = ColorHandler.randomize_color()
        self.label.config(text=f"Selected Color: {random_color}")
    
    def reset_defaults(self):
        pass