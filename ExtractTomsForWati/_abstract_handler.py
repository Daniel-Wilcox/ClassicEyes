from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pandas as pd
import os

@dataclass
class AbstractHandler(ABC):

    # Initialize file attributes
    file_path: str|None = field(default = None)
    save_path: str|None = field(default = None)
    valid_file_types: list[str] = field(default_factory = list, init = False)


    def __str__(self):
        return f"{self.__class__.__name__}".removesuffix("Handler")
    
    # @abstractmethod
    # def load_dataframe(self):
    #     pass #! Change to normal method and not abstract

    def load_dataframe(self, filepath: str|None = None):
        """Data is read into class variables from provided filepath"""


        # self.file_path = filepath or getattr(self, "file_path", None) or self._gen_filepath_from_filepath()
        # saver = self.save_path

        
        # if not hasattr(self, "save_path") and not self.save_path:
        #     # No self.save_path
        #     if not savepath:
        #         self.save_path = savepath # Update self.save_path based on provided savepath
        #     else:
        #         self.save_path = self._gen_savepath_from_filepath() # Update self.save_path based on stored self.filepath
        # save = self.save_path



        if not hasattr(self, "file_path"):
            raise AttributeError("Missing 'file_path' attribute. ")
        filepath = self.file_path

        # Ensure that file_path is set properly
        if filepath and not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        self.file_path = filepath

        # Check file types
        file_name = filepath.split('/')[-1]
        file_type = file_name.split('.')[-1]

        if not(f".{file_type}" in self.valid_file_types):
            raise ValueError(
                f"{file_name} does not have valid file type: {self.valid_file_types}."
            )

        df = pd.read_excel(filepath, header = None)
        self.df_raw = df


    @abstractmethod
    def process_data(self, filepath:str):
        """Data in class variables is transformed"""
        pass

    @abstractmethod
    def save_data(self, savepath:str):
        """Save the cleaned data to a new file in save_folder."""
        pass
    
    @abstractmethod
    def load_and_process(self, filepath):
        """The main method to run the complete handler workflow."""
        pass

    @abstractmethod
    def load_process_save(self, filepath):
        """The main method to run the complete handler workflow."""
        pass


if __name__ == "__main__":
    print(AbstractHandler)