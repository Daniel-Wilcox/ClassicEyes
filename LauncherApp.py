import sys
import tkinter as tk
import os
import importlib.util
# from app_files.pages.AbstractPage import AbstractPage
from app_files import AbstractPage, AbstractHandler


class LaunchApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Define init defaults
        self.root_path = os.getcwd()
        self.app_files_path = os.path.join(self.root_path, "app_files")
        self.all_pages_path = os.path.join(self.app_files_path, "pages")
        self.all_handlers_path = os.path.join(self.app_files_path, "handlers")

        #! Change to a separate module 'load_homepage'
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

        # Initializing pages to an empty array
        application_page_list = self.get_page_classes()
        print(f"{application_page_list = }")
        print(f"{application_page_list[0].__name__ = }")

        self.app_pages = {
            SinglePageClass.__name__: SinglePageClass(parent = self.main_page, controller = self)
            for SinglePageClass in application_page_list
        }

        # Place all pages on grid
        for page in self.app_pages.values():
            page.grid(row = 0, column = 0, sticky ="nsew")

        # Get the first page in the list of pages and show it as the starting page
        first_page = self.app_pages.get("HomePage", next(iter(application_page_list)))
        self.show_page(first_page)

        
    def import_from_filepath(self, module_name: str, filepath: str):

        print(f"Importing: {module_name}")
        # Validate the provided path
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Module '{module_name}' doesn't exists at {filepath}.")

        # Create a module spec from the file path
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None:
            raise ImportError(f"Couldn't load spec for module {module_name}' from '{filepath}'")

        # Create a new module based on the spec
        module = importlib.util.module_from_spec(spec)

        # Execute the module (this runs the file)
        # if not spec.loader:
        #     raise ImportError(f"Could not load module '{module_name}' from '{filepath}'")

        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    



    def get_page_classes(self) -> list[AbstractPage]:
        """Dynamically load all pages from the "app_files/pages" directory."""

        # Get list of module names (filename without extension)
        python_page_files = [
                os.path.splitext(page_name)[0]
                for page_name in os.listdir(self.all_pages_path) 
                if page_name.endswith(".py") and not page_name.startswith("_") and not page_name.startswith("Abstract")
            ]
    
        
        # Load each module and append to list
        page_classes = []

        for module_name in python_page_files:
            module = self.import_from_filepath(
                module_name, os.path.join(self.all_pages_path, f"{module_name}.py")
            )

            # Extract the class (assuming class name matches module name)
            page_class = getattr(module, module_name, None)
            if page_class is not None and issubclass(page_class, AbstractPage):
                page_classes.append(page_class)
            else:
                raise ImportError(f"Module '{module_name}' does not contain a valid page class derived from AbstractPage.")

        return page_classes


    def show_page(self, page_name):
        """Show a frame for the given page name."""
        page = self.app_pages[page_name]
        page.tkraise()

if __name__ == "__main__":
    app = LaunchApp()
    app.mainloop()
