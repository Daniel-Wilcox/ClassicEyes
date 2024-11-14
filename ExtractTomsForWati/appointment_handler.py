from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from ._abstract_handler import AbstractHandler



### Constants and Defaults ###
#! TODO: ensure all known junk words are provided
REMOVE_ROWS_WITH_KEYWORDS = [
    'C/Lens Check',
    'Funded Accounts',
    'Private Accounts',
    'C/Lens Purchases',
    'Follow up Exam',
    'Spec Exam',
]

#! TODO: Add in the full list of Optometrists
VALID_OPTOMETRIST_LIST = [
    "Nicci Wilcox",
    "Amisha Soodyall",
    "Sandesh Srikissoon",
]

#? CAN_CHANGE: These are the headings of the final dataframe, free to changeAdd in the full list of Optometrists
DEFAULT_CHOSEN_HEADINGS = [
    "Date",
    "Time",
    "Name",
    "Cell",
    "Optometrists",
]


DEFAULT_VALID_FILE_TYPES= [
    ".xls", 
    ".xlsx"
]



@dataclass
class AppointmentHandler(AbstractHandler):

    # Initialize file attributes
    #! Overwrite expected attributes to be defined within child class
    valid_file_types: list[str] = field(default_factory = lambda: DEFAULT_VALID_FILE_TYPES)

    #* Initialize child class's additional default attributes defined
    valid_optometrist_list: list[str] = field(default_factory = lambda: VALID_OPTOMETRIST_LIST)
    remove_rows_containing_list: list[str] = field(default_factory = lambda: REMOVE_ROWS_WITH_KEYWORDS)
    default_headings_list: list[str] = field(default_factory = lambda: DEFAULT_CHOSEN_HEADINGS)

    #* ---------------------
    #* Transform data methods
    #* ---------------------
    def _assign_optometrist(self, x):
        """Assign optometrist to patient row in considered DataFrame"""
        if x in self.valid_optometrist_list:
            return x
        else:
            return np.nan

    def _validate_dataframe(self, df_attr: str = "df_raw", df: pd.DataFrame | None = None):

        # Set temporary DataFrame on provided DataFrame or DataFrame stored in the class attribute
        df_temp =  df if df is not None else getattr(self, df_attr, None)

        if df_temp is None:
            msg = f"Missing '{df_attr}' attribute. Cannot clean data unless data is imported with 'load_dataframe' method."
            raise AttributeError(msg)
        
        return df_temp
    
    # @abstractmethod
    def _clean_data(self, df: pd.DataFrame|None = None):

        # Retrieve relevant dataframe and validate
        self.df_raw = self._validate_dataframe("df_raw", df)
        df_raw = self.df_raw.copy()

        #* Clean up Excel:
        # Drop all empty rows and last row (page X of Y)
        df_clean = df_raw.iloc[:-1].dropna(how='all').reset_index(drop=True)

        # Remove all non-useful header rows (first 5)
        df_clean = df_clean.iloc[6:].reset_index(drop=True)

        # Remove all rows with known key words from first column
        data_mask = df_clean.loc[:, 0].isin(self.remove_rows_containing_list)
        df_clean = df_clean[~data_mask].reset_index(drop=True)

        # Remove all empty columns and rename headings based on first rows cells
        df_clean = df_clean.dropna(axis=1, how='all')
        df_clean.columns = df_clean.iloc[0]  # Assign row 0 to be the new headers
        df_clean = df_clean.drop(0).reset_index(drop=True)

        dropped_columns = df_clean.columns.notna()
        df_clean = df_clean.loc[:, dropped_columns]

        # Assign optometrist to patient
        df_clean["Optometrists"] = df_clean["Date"].apply(lambda x: self._assign_optometrist(x)).ffill()
        df_clean["Date"] = df_clean["Date"].ffill()

        # Fix Date Column
        date_mask = pd.to_datetime(df_clean["Date"], format="%Y-%m-%d", errors="coerce").notnull()
        df_clean = df_clean[date_mask].reset_index(drop=True)

        # Fix Name column
        df_clean["Name"] = df_clean["Name"].str.title()

        # Assign class attribute with resulting DataFrame
        self.df_clean = df_clean

        return df_clean

    # @abstractmethod
    def _add_features(self, df: pd.DataFrame | None = None):

        # Retrieve relevant dataframe and validate
        self.df_clean = self._validate_dataframe("df_clean", df)
        df_clean = self.df_clean.copy()


        self.df_clean =  df if df is not None else getattr(self, "df_clean", None)
        df_clean = self.df_clean.copy()

        # Add country code column
        #! Change phone numbers to include country code
        #TODO Add new features here

        self.df_clean = df_clean
        return df_clean

    # @abstractmethod
    def _extract_features(self, df: pd.DataFrame | None = None):

        # Retrieve relevant dataframe and validate
        self.df_clean = self._validate_dataframe("df_clean", df)
        df_clean = self.df_clean.copy()

        # !Extract desired features here
        df_output = df_clean[self.default_headings_list].copy() 
        self.df_output = df_output 

        return df_output

    # @abstractmethod
    def save_data(self, savepath: str|None = None):
        """Save the cleaned data to a new file in save_folder."""

        # Check for file_path availability
        if not hasattr(self, "file_path"):
            raise AttributeError("Missing 'file_path' attribute. Cannot save data unless import data filepath is available.")

        # Set for save_path based on availability
        self.save_path = savepath or getattr(self, "save_path", None) or self._get_savepath_from_filepath()
        # self.save_path = savepath if savepath is not None else getattr(self, "save_path", None) 
        # if not self.save_path is None:
        #     self.save_path = self._get_savepath_from_filepath()

        # Check output DataFrame availability 
        if not hasattr(self, "df_output"):
            raise AttributeError("Missing 'df_output' attribute. Cannot save data unless data is provided.")
        
        # Get output pd.DataFrame and save
        self.df_output.to_csv(self.save_path, index=False)


if __name__ == "__main__":
    appointment_handler = AppointmentHandler()


    #! --------------------------
    #! DATA OUTPUT EXPECTATIONS
    #! --------------------------
    # Number: 27832319744
    # Name: Daniel Wilcox
    # Date: 13/11/2024
    # Time: 9:30
    # Practice: CE PV (next door to Pick 'n Pay)
    # Optometrist: Nicci Wilcox
    #! --------------------------




