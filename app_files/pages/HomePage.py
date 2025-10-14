import tkinter as tk
from .AbstractPage import AbstractPage
# from pages import AbstractPage

class HomePage(AbstractPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        self.label = tk.Label(self, text="Home Page", font=('Helvetica', 16))
        
        self.page1_button = tk.Button(self, text="Go to Page 1", 
                                 command=lambda: controller.show_page('Page1'))

        self.page2_button = tk.Button(self, text="Go to Page 2", 
                                 command=lambda: controller.show_page('Page2'))

    def load_widgets(self):
        self.label.pack(pady=10)
        self.page1_button.pack(pady=10)
        self.page2_button.pack(pady=10)




    def reset_defaults(self):
        pass




if __name__ == "__main__":
    home = HomePage()

    print(f"{home = }")
    print(f"{str(home) = }")
    print(f"{home.__name__ = }")
    print(f"{home.__str__ = }")
    print(f"{home.__repr__ = }")



