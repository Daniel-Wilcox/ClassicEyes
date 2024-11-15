from abc import ABC, abstractmethod
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd

from ExtractTomsForWati import AbstractHandler, AppointmentHandler, BirthdayHandler


#!  TODO ADD WATI API connector 
#! https://docs.wati.io/reference/post_api-v1-sendtemplatemessages



# Constants:    #
# ------------- #
ALL_WATI_HANDLERS_LIST = [
    AppointmentHandler, #! NEED TO ADD MORE HANDLER CLASSES
    BirthdayHandler,
] 
WATI_TEMPLATE_DICT = {
    cls.__name__.removesuffix("Handler") : cls 
    for cls in ALL_WATI_HANDLERS_LIST
}

CE_PRACTICE_LIST = [
    "Pavilion",
    "La Lucia"
]

# Page definitions:    #
# -------------------- #
class AbstractPage(tk.Frame, ABC):

    def __init__(self, parent, controller):
        super().__init__(parent)

        # Providing the access to Application's functions. i.e. the ability to change page.
        self.controller = controller

        # Define page's default variables
        self.reset_defaults()

        # Populate page with widgets
        self.load_widgets()

    @abstractmethod
    def load_widgets(self):
        """Define page's widgets to be displayed. Defaults are defined in 'reset_defaults' function."""
        pass

    @abstractmethod
    def reset_defaults(self):
        """Define all default variables to be used on page."""
        pass


class Application(tk.Tk):

    def __init__(self, application_page_list: list[AbstractPage]):
        super().__init__()

        if not application_page_list:
            raise ValueError("Application must have pages provided.")

        # Define window properties
        self.title("Extract Contacts for Wati Templates")
        self.geometry("400x400")
        self.focus_force()
        self.eval('tk::PlaceWindow . center')
        # self.iconbitmap("filepath_to_icon")

        # Define Shared properties
        self.is_processing = False
        self.SelectedHandler: AbstractHandler|None = None

        # Create main page and add in other pages
        self.main_page = tk.Frame(self)
        self.main_page.pack(side = "top", fill = "both", expand = True) 
        self.main_page.grid_rowconfigure(0, weight = 1)
        self.main_page.grid_columnconfigure(0, weight = 1)

        # Initializing pages to an empty array
        self.app_pages = {
            SinglePageClass: SinglePageClass(parent = self.main_page, controller = self)
            for SinglePageClass in application_page_list
        }
        # Place all pages on grid
        for page in self.app_pages.values():
            page.grid(row = 0, column = 0, sticky ="nsew")

    
        # Show first page
        first_page = next(iter(application_page_list))
        self.show_page(first_page, reset_defaults=False)

    def show_page(self, page_class, reset_defaults=True):
        page: AbstractPage
        page = self.app_pages[page_class]

        if reset_defaults:
            page.reset_defaults()
        
        page.tkraise()


class HomePage(AbstractPage):

    def __init__(self, parent, controller):
        self.template_list = list(WATI_TEMPLATE_DICT.keys())
        super().__init__(parent, controller)

    def load_widgets(self):

        # Dropdown menu for message template type
        # self.template_label = tk.Label(self, text=self.template_label_default.get())
        self.template_label = tk.Label(self, textvariable=self.template_label_default)
        self.template_label.pack(pady = 10)
        self.template_menu = tk.OptionMenu(self, self.template_default, *self.template_list)
        self.template_menu.pack(pady = 5)

        # Dropdown menu for Classic Eyes Practice
        self.practice_label = tk.Label(self, text=self.practice_label_default.get())
        self.practice_label.pack(pady = 10)
        self.practice_menu = tk.OptionMenu(self, self.practice_default, *CE_PRACTICE_LIST)
        self.practice_menu.pack(pady = 5)

        # File upload space
        self.file_label = tk.Label(self, text=self.file_label_default.get())
        self.file_label.pack(pady = 10)
        self.upload_button = tk.Button(self, text = "Select File", command = self._update_uploaded_filename)
        self.upload_button.pack(pady = 5)
        self.file_path_label = tk.Label(self, text = self.file_path_label_default.get())
        self.file_path_label.pack(pady = 5)
        
        # Process button
        self.process_button = tk.Button(self, text = "Process File", command = self._validate_and_process)
        self.process_button.pack(pady = 20)

    def _update_uploaded_filename(self):
        file_path = filedialog.askopenfilename(title = "Select a file", filetypes = [("All Files", "*.*")])
        if file_path:
            self.selected_filepath = file_path
            self.file_path_label.config(text = f"Selected: {file_path.split('/')[-1]}")
    
    def _validate_and_process(self):

        # Get user selected variables/uploaded files and check if valid input
        selected_template = self.template_default.get()
        if not selected_template:
            messagebox.showwarning("Variable Missing", "Please select Wati Template before processing.")
            return
        
        selected_practice = self.practice_default.get()
        if not selected_practice:
            messagebox.showwarning("Variable Missing", "Please select Classic Eyes Practice before processing.")
            return
        
        selected_filepath = self.selected_filepath
        if not selected_filepath:
            messagebox.showwarning("File Missing", "Please upload a TOMs Excel Report file before processing.")
            return

        # Move to the loading screen
        self.controller.show_page(LoadingPage)
        self.controller.app_pages[LoadingPage]._start_loading()
 
        # Get Handler and supply selected practice
        process_handler = WATI_TEMPLATE_DICT[selected_template](selected_practice = selected_practice)
        self.controller.SelectedHandler = process_handler

        # Start processing in a new thread to avoid freezing the UI
        self.processing_thread = threading.Thread(
            target = self._process_file_with_handler,
            args = (process_handler, selected_filepath)
        )
        self.processing_thread.start()

        # Somehow make sure that when cancel is pressed that the process is killed
        self.controller.is_processing = True

        # Start checking for the thread's completion
        self._check_thread()

    def _check_thread(self):
        alive_thread = self.processing_thread.is_alive()
        is_processing = self.controller.is_processing

        if alive_thread and is_processing:
            self.after(100, self._check_thread)

        elif alive_thread and not is_processing:
            self.controller.app_pages[LoadingPage]._stop_loading() 
            self.controller.app_pages[HomePage].reset_defaults()
            self.controller.show_page(HomePage)
        else:
            self._completed_process_callback()

    def _process_file_to_template(self, selected_template: str, selected_practice: str):

        try:
            # Call the appropriate template function
            template_function = WATI_TEMPLATE_DICT[selected_template]
            handle_output = template_function(selected_template, selected_practice)

            # Store function output
            self.controller.handle_output = handle_output 

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    def _process_file_with_handler(self, process_handler: AbstractHandler, file_path: str):
        # Apply appropriate Handler class with 
        handle_output = process_handler.load_and_process(filepath = file_path)

        # Store function output
        self.controller.handle_output = handle_output 

    def _completed_process_callback(self):
        # Only when callback is 
        self.controller.app_pages[LoadingPage]._stop_loading() 
        self.controller.show_page(DownloadPage)

    def reset_defaults(self):
        # Reset Handler information in application
        self.controller.SelectedHandler = None
        self.controller.handle_output = None

        # Dropdown menu for message template type
        self.template_label_default = tk.StringVar(value="Select Wati Template Type")
        self.template_default = tk.StringVar(value=next(iter(self.template_list)))

        # Dropdown menu for Classic Eyes Practice
        self.practice_label_default = tk.StringVar(value="Select Classic Eyes Practice")
        self.practice_default = tk.StringVar(value=next(iter(CE_PRACTICE_LIST)))

        # File upload space
        self.file_label_default = tk.StringVar(value="Upload Relevant TOM's Report")
        self.file_path_label_default = tk.StringVar(value="No file selected")

        if hasattr(self, 'file_path_label'):
            self.file_path_label.config(text = self.file_path_label_default.get())
            
        self.selected_filepath = None
   
class LoadingPage(AbstractPage):
    
    def load_widgets(self):
        """Define page's widgets to be displayed. Defaults are defined in 'reset_defaults' function."""
        # Add a label to indicate loading
        self.loading_label = tk.Label(self, text = "Processing... Please wait")
        self.loading_label.pack(pady = 20)

        # Add the ttk Progressbar in 'indeterminate' mode
        self.progress = ttk.Progressbar(self, orient = "horizontal", mode = "indeterminate")
        self.progress.pack(fill = "x", padx = 20, pady = 20)
        # self._start_loading()

        # Add a cancel button if needed
        self.cancel_button = tk.Button(self, text="Cancel", command=self._cancel_process)
        self.cancel_button.pack(pady = 10)

    def reset_defaults(self):
        """Define all default variables to be used on page."""
        pass
        
    def _start_loading(self):
        self.progress.start(50)

    def _stop_loading(self):
        self.progress.stop()

    def _cancel_process(self):
        self.progress.stop()
        self.controller.is_processing = False
        self.controller.app_pages[HomePage].reset_defaults()
        self.controller.show_page(HomePage)

class DownloadPage(AbstractPage):
    
    def load_widgets(self):
        self.complete_label = tk.Label(self, text = "Processing Complete!")
        self.complete_label.pack(side = "top", fill = "x", pady = 10)

        self.download_button_1 = tk.Button(
            self, text="Save As", command= lambda: self._download_results(ask_user=True)
        )
        self.download_button_1.pack(pady=10)

        self.download_button_2 = tk.Button(
            self, text="Auto Save", command= lambda: self._download_results(ask_user=False)
        )
        self.download_button_2.pack(pady=10)

        self.generate_another_button = tk.Button(
            self, 
            text = "Generate Another", 
            command=self._generate_another
        )
        self.generate_another_button.pack(pady=10)

    def _download_results(self, ask_user: bool = False):

        # Get data/handler 
        process_handler: AbstractHandler = self.controller.SelectedHandler
        handle_output: pd.DataFrame | str | None = self.controller.handle_output

        if handle_output is None or handle_output.empty:
            messagebox.showwarning("No Results", "There are no results to download.")

        if ask_user:
            # Slow Save - Ask user for name and location
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        else:
            # Quick Save - Datetime convention
            save_path = None

        process_handler.save_data(savepath = save_path)

        show_save = save_path or process_handler.save_path
        show_save_name = show_save.split("/")[-1]
        messagebox.showinfo("Download", f"File {show_save_name} successfully saved at {show_save}.")

        # Clear screen and return home
        self._generate_another()


    def _generate_another(self):
        # Clear screen and return home
        self.controller.app_pages[HomePage].reset_defaults()
        self.controller.show_page(HomePage)
    
    def reset_defaults(self):
        pass

        


def main():
    page_list = [HomePage, LoadingPage, DownloadPage]
    app = Application(application_page_list = page_list)
    app.mainloop()

    return 


if __name__ == "__main__":
    main()
