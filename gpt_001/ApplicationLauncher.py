# ApplicationLauncher.py

import tkinter as tk
import os
import sys
import importlib.util
from app_files.pages.AbstractPage import AbstractPage
# from app_files.pages.HomePage import HomePage
from utils import check_for_update, download_latest_files


def resource_path(relative_path):

    try:
        root_path = sys._MEIPASS
    except Exception:
        root_path = os.path.abspath(".")

    return os.path.join(root_path, relative_path)

class HomePage2(AbstractPage):

    def __init__(self, parent, controller):
        # self.is_homepage = True
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



class LaunchApp(tk.Tk):
    def __init__(self, root_path:str):
        super().__init__()

        # Define init defaults          
        self.root_path = root_path if root_path is not None else resource_path("")
        self.app_files_path = os.path.join(self.root_path, "app_files")
        self.all_pages_path = os.path.join(self.app_files_path, "pages")
        self.all_handlers_path = os.path.join(self.app_files_path, "handlers")

        # Check for updates and download the latest files if necessary
        if check_for_update():
            download_latest_files()

        # Define window properties
        self.title("Classic Eyes Application Launcher")
        self.geometry("400x400")
        self.focus_force()
        self.eval("tk::PlaceWindow . center")

        # Container to hold all the pages
        self.main_page = tk.Frame(self)
        self.main_page.pack(side="top", fill="both", expand=True)
        self.main_page.grid_rowconfigure(0, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)

        # Load pages
        print(f"Loading Pages:")
        # self.app_pages = self.load_pages() # {page_name: PageClass(parent=self.main_page, controller=self)}
        self.application_page_list = self.load_pages() # [page_name]
        self.app_pages = {
            SinglePageClass.__name__: SinglePageClass(parent = self.main_page, controller = self)
            for SinglePageClass in self.application_page_list 
        }

        # Place all pages on grid
        for page in self.app_pages.values():
            page.grid(row = 0, column = 0, sticky ="nsew")


        print(f"Loaded pages: {self.app_pages.keys()}")
        

        # Set the first page to HomePage (or raise an error if not found)
        self.default_first_page = self.get_home_page()
        self.show_page(self.default_first_page)


    def get_home_page(self):

        home_classes = {
            page_name:page_class
            for page_name, page_class in self.app_pages.items()
            if getattr(page_class, "is_homepage", False)            
        }  
        
        if not home_classes:
            print(f"No is_homepage attributes available, setting first from app_pages as default first page")
            home_classes = next(iter(self.app_pages))

        elif len(home_classes) > 1:
            raise ValueError(f"Too many pages marked as home page: {[name for name in home_classes.keys()]}")

        default_first_page = next(iter(list(home_classes.keys())))
        print(f"Assigning {default_first_page} as the default first page.")
        
        return default_first_page
        
    def import_from_filepath(self, module_name: str, filepath: str):
        """Import a module dynamically from a file path."""
        filepath = os.path.abspath(filepath)
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        print(f"Loading {module_name} module")
        return module


    def load_pages(self):
        """Dynamically load all pages from the 'app_files/pages' directory."""
        
        python_page_files = [
            os.path.splitext(page_name)[0]
            for page_name in os.listdir(self.all_pages_path)
            if page_name.endswith(".py") and not page_name.startswith("_") and not page_name.startswith("Abstract")
        ]

        print(f"{python_page_files = }")
        
        page_classes = []

        for module_name in python_page_files:
            # Import each page module dynamically
            print(f"importing '{module_name}' from '{os.path.join(self.all_pages_path, f"{module_name}.py")}'")
            module = self.import_from_filepath(module_name, os.path.join(self.all_pages_path, f"{module_name}.py"))

            # Extract class
            page_class = getattr(module, module_name, None)
            print(f"{page_class = }")
            print(f"{page_class.__name__ = }")
            
            if not (page_class and issubclass(page_class, AbstractPage)):
                raise ImportError(f"Module '{module_name}' does not contain a valid page class derived from AbstractPage.")
            page_classes.append(page_class)


        # Return the loaded page classes
        return page_classes
    

    def show_page(self, page_name: str):
        """Display a specific page."""
        page: AbstractPage

        try:
            page = self.app_pages[page_name]
        except Exception as e:
            raise ValueError(f"Page '{page_name}' not found in app_pages.")
        
        page.tkraise()



if __name__ == "__main__":

    import config, utils

    # try:
    #     app = LaunchApp(root_path = os.path.dirname(__file__))
    #     app.mainloop()
    # except Exception as exc:
    #     print(f"MAJOR FAULT: \n{30*'='}\n{exc}")
    #     raise exc
    

    if getattr(sys, 'frozen', False):
        # If running as a bundled app
        print(f"Using executable path")
        root_path = os.path.dirname(sys.executable)
    else:
        # If running in a normal Python environment
        print(f"Using file path path")
        root_path = os.path.dirname(__file__)

    print(f"{root_path = }")

    app = LaunchApp(root_path = root_path)
    app.mainloop()
    
    
    