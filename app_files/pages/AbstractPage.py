from abc import ABC, abstractmethod
import tkinter as tk


class AbstractPage(tk.Frame, ABC):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Providing the access to Application"s "show_page" method. i.e. the ability to change page.
        self.controller = controller

        # Define page"s default variables
        self.reset_defaults()

        # Populate page with widgets
        self.load_widgets()

    @abstractmethod
    def load_widgets(self):
        """Define page"s widgets to be displayed. Defaults are defined in "reset_defaults" function."""
        pass

    @abstractmethod
    def reset_defaults(self):
        """Define all default variables to be used on page."""
        pass