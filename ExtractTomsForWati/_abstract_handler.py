import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd


@dataclass(kw_only=True)
class AbstractHandler(ABC):
    # Initialize file attributes
    file_path: str | None = field(default=None)
    save_path: str | None = field(default=None)
    valid_file_types: list[str] = field(
        default_factory=list, init=False
    )  #! Expected to be defined in child

    # Initialize pd.DataFrame attributes
    df_raw: pd.DataFrame | None = field(default=None)
    df_clean: pd.DataFrame | None = field(default=None)
    df_output: pd.DataFrame | None = field(default=None)

    # Initialize other attributes
    selected_practice: str | None = field(default=None)

    def __str__(self):
        return f"{self.__class__.__name__}".removesuffix("Handler")

    # * ---------------------
    # * Loading data methods
    # * ---------------------
    def load_dataframe(self, filepath: str | None = None):
        """Loads a DataFrame from the provided file path or the class attribute file_path."""
        filepath = self._get_filepath(filepath)
        self._validate_filepath(filepath)
        self.df_raw = self._load_file(filepath)
        return

    def _get_filepath(self, filepath: str | None):
        """Resolve and return the file path, prioritizing the argument over the class attribute."""
        this_filepath = (
            filepath if filepath is not None else getattr(self, "file_path", None)
        )

        if not this_filepath:
            raise AttributeError("No valid 'file_path' provided or set in the class.")
        self.file_path = this_filepath

        return this_filepath

    def _validate_filepath(self, filepath: str | None = None):
        """Validate that the file exists and has a valid type."""

        # Validate provided or class attribute depending on availability
        this_filepath = (
            filepath if filepath is not None else getattr(self, "file_path", None)
        )

        if not os.path.exists(filepath) or not this_filepath:
            raise FileNotFoundError(f"File not found at: {filepath}")

        file_ext = os.path.splitext(filepath)[-1]  # File extension
        if file_ext not in self.valid_file_types:
            raise ValueError(
                f"Invalid file type '{file_ext}'. Expected one of {self.valid_file_types}."
            )

    def _load_file(self, filepath: str) -> pd.DataFrame:
        """Load the file into a DataFrame. This can be overridden by subclasses."""
        return pd.read_excel(filepath, header=None)

    def _validate_dataframe(
        self, df_attr: str = "df_raw", df: pd.DataFrame | None = None
    ):
        # Set temporary DataFrame on provided DataFrame or DataFrame stored in the class attribute
        df_temp = df if df is not None else getattr(self, df_attr, None)

        if df_temp is None:
            msg = f"Missing '{df_attr}' attribute. Cannot clean data unless data is imported with 'load_dataframe' method."
            raise AttributeError(msg)

        return df_temp

    # * ---------------------
    # * Transform data methods
    # * ---------------------
    def transform_data(self):
        """Data in class variables is transformed"""
        self._clean_data()
        self._add_features()
        self._extract_features()

        return self.df_output

    @abstractmethod
    def _clean_data(self, df: pd.DataFrame | None = None):
        """Abstract method for cleaning data. Must be implemented by subclasses. It is recommended to use the following as the start of the method when implemented so that you can use the `transform_data` method correctly.

        ## Recommended initial code for `_clean_data` method.

        Retrieve relevant dataframe and validate

        ```python
        self.df_raw = self._validate_dataframe("df_raw", df)
        df_raw = self.df_raw.copy()
        ```

        """
        pass

    @abstractmethod
    def _add_features(self, df: pd.DataFrame | None = None):
        """Abstract method for adding features.. Must be implemented by subclasses. It is recommended to use the following as the start of the method when implemented so that you can use the `transform_data` method correctly.

        ## Recommended initial code for `_clean_data` method.

        Retrieve relevant dataframe and validate

        ```python
        self.df_raw = self._validate_dataframe("df_raw", df)
        df_raw = self.df_raw.copy()
        ```

        """

        pass

    def _extract_features(
        self, df: pd.DataFrame | None = None, headings: list | None = None
    ):
        # Retrieve df_clean dataframe and validate
        # df_clean is ALWAYS the final data before output
        self.df_clean = self._validate_dataframe("df_clean", df)
        df_clean = self.df_clean.copy()

        # Extract desired features
        if not headings:
            df_output = df_clean.copy()
        else:
            df_output = df_clean[headings].copy()

        self.df_output = df_output

        return df_output

    # * ---------------------
    # * Save data methods
    # * ---------------------
    def _get_savepath_from_filepath(self) -> str:
        filepath = getattr(self, "file_path", None)
        if not filepath:
            raise AttributeError("Missing 'file_path' attribute.")

        # Create datetime based filename for save file
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        handler_name = str(self)
        new_filename = f"{handler_name}_{current_datetime}.csv"

        # Create save path by adding new filename to filepath
        dir_path = os.path.dirname(filepath)
        savepath = os.path.join(dir_path, new_filename)
        self.save_path = savepath

        return savepath

    @abstractmethod
    def save_data(self, savepath: str):
        """Save the cleaned data to a new file in save_folder."""
        pass

    # * ---------------------
    # * Apply Flows to data methods
    # * ---------------------
    def load_and_process(self, filepath: str) -> pd.DataFrame:
        """The main method to run the partial handler workflow i.e. Load and Process Data."""

        self.load_dataframe(filepath)
        self.transform_data()

        return self.df_output

    def load_process_save(self, filepath: str, savepath: str | None = None):
        """The main method to run the complete handler workflow."""

        self.load_dataframe(filepath)
        self.transform_data()
        self.save_data(savepath)


if __name__ == "__main__":
    print(AbstractHandler)
