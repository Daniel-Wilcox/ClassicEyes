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
    
    #* ---------------------
    #* Loading data methods
    #* ---------------------
    # @abstractmethod
    # def load_dataframe(self):
    #     pass #! Change to normal method and not abstract
    
    def load_dataframe(self, filepath: str | None = None):
        """Loads a DataFrame from the provided file path or the class attribute file_path."""
        filepath = self._get_filepath(filepath)
        self._validate_filepath(filepath)
        self.df_raw = self._load_file(filepath)
        return

    def _get_filepath(self, filepath: str | None):
        """Resolve and return the file path, prioritizing the argument over the class attribute."""
        this_filepath = filepath or getattr(self, "file_path", None)
                                            
        if not this_filepath:
            raise AttributeError("No valid 'file_path' provided or set in the class.")
        self.file_path = this_filepath

        return this_filepath

    def _validate_filepath(self, filepath: str | None = None):
        """Validate that the file exists and has a valid type."""

        # Validate provided or class attribute depending on availability
        this_filepath = filepath or getattr(self, "file_path", None)

        if not os.path.exists(filepath) or not this_filepath:
            raise FileNotFoundError(f"File not found at: {filepath}")
        
        file_ext = os.path.splitext(filepath)[-1] # File extension
        if file_ext not in self.valid_file_types:
            raise ValueError(f"Invalid file type '{file_ext}'. Expected one of {self.valid_file_types}.")

    def _load_file(self, filepath: str) -> pd.DataFrame:
        """Load the file into a DataFrame. This can be overridden by subclasses."""
        return pd.read_excel(filepath, header = None)



    #* ---------------------
    #* Process data methods
    #* ---------------------
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

