from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import os
import pandas as pd

from ._abstract_handler import AbstractHandler



# ### Constants and Defaults ###
# #! TODO: ensure all known junk words are provided
# REMOVE_ROWS_WITH_KEYWORDS = [
#     'C/Lens Check',
#     'Funded Accounts',
#     'Private Accounts',
#     'C/Lens Purchases',
#     'Follow up Exam',
#     'Spec Exam',
# ]

# #! TODO: Add in the full list of Optometrists
# VALID_OPTOMETRIST_LIST = [
#     "Nicci Wilcox",
#     "Amisha Soodyall",
#     "Sandesh Srikissoon",
# ]

# #? CAN_CHANGE: These are the headings of the final dataframe, free to changeAdd in the full list of Optometrists
# DEFAULT_CHOSEN_HEADINGS = [
#     "Date",
#     "Time",
#     "Name",
#     "Cell",
#     "Optometrists",
# ]


DEFAULT_VALID_FILE_TYPES= [
    ".xls", 
    ".xlsx"
]



@dataclass
class BirthdayHandler(AbstractHandler):

    # Initialize file attributes
    valid_file_types: list[str] = field(default_factory = lambda: DEFAULT_VALID_FILE_TYPES)

    # # Initialize pd.DataFrame attributes
    # df_raw: pd.DataFrame | None = field(default = None)
    # df_clean: pd.DataFrame | None = field(default = None)
    # df_output: pd.DataFrame | None = field(default = None)

    # # Initialize Default attributes
    # valid_optometrist_list: list[str] = field(default_factory = lambda: VALID_OPTOMETRIST_LIST)
    # remove_rows_containing_list: list[str] = field(default_factory = lambda: REMOVE_ROWS_WITH_KEYWORDS)
    # default_headings_list: list[str] = field(default_factory = lambda: DEFAULT_CHOSEN_HEADINGS)


    def load_dataframe(self):
        """Data is read into class variables from provided filepath"""

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

    
    def _assign_optometrist(self, x):
        if x in self.valid_optometrist_list:
            return x
        else:
            return np.nan


    def _clean_data(self, df:pd.DataFrame|None = None):
        
        # Check whether to use provided DataFrame or class provided DataFrame in self.df_raw
        if not hasattr(self, "df_raw") or self.df_raw is None:
            # If doesn't exist or if self.df_raw = "" or self.df_raw = None
            
            if not df:
                self.df_raw = df.copy() # Update 'self.df_raw' to consider provided DataFrame 

            else:
                raise AttributeError(
                    "Missing 'df_raw' attribute. Cannot clean data unless data is imported with 'load_dataframe' method."
                )
        
        df_raw = self.df_raw.copy()

        ### Clean up Excel: ###
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

        self.df_clean = df_clean

        return df_clean


    def _add_features(self, df:pd.DataFrame|None = None):

        # Check whether to use provided DataFrame or class provided DataFrame in self.df_clean
        if not hasattr(self, "df_clean") or self.df_clean is None:            
            if not df:
                self.df_clean = df.copy() # Update 'self.df_raw' to consider provided DataFrame 
            else:
                raise AttributeError(
                    "Missing 'df_clean' attribute. Cannot add features to data unless data is imported with 'load_dataframe' method."
                )
    
        df_clean = self.df_clean.copy()


        # !Add new features here
        ...


        self.df_clean = df_clean
        return df_clean

    
    def _extract_features(self, df:pd.DataFrame|None = None):

        # Check whether to use provided DataFrame or class provided DataFrame in self.df_clean
        if not hasattr(self, "df_clean") or self.df_clean is None:            
            if not df:
                self.df_clean = df.copy() # Update 'self.df_raw' to consider provided DataFrame 
            else:
                raise AttributeError(
                    "Missing 'df_clean' attribute. Cannot add features to data unless data is imported with 'load_dataframe' method."
                )
    
        df_clean = self.df_clean.copy()

        # !Extract desired features here
        df_output = df_clean[self.default_headings_list].copy() 
        self.df_output = df_output 

        return df_output


    def process_data(self):
        """Data in class variables is transformed"""

        # Clean Data
        self._clean_data()

        # Apply new features
        self._add_features()

        # Extract Data
        self._extract_features() 

        df = self.df_output

        return df

        
    def _gen_savepath_from_filepath(self) -> str:

        if not hasattr(self, "file_path"):
            raise AttributeError("Missing 'file_path' attribute.")
        
        filepath = self.file_path

        if not filepath:
            raise ValueError("Value of 'file_path' cannot be None. Please provide filepath correctly.")


        # Create datetime based filename for save file
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_filename = f"Appointments_{current_datetime}.csv"
    
        new_filepath = filepath.split('/')[:-1]
        new_filepath.append(new_filename)

        savepath = "/".join(new_filepath)
        self.save_path = savepath

        return savepath


    def save_data(self, savepath: str|None = None):
        """Save the cleaned data to a new file in save_folder."""

        # Check for file_path availability
        if not hasattr(self, "file_path"):
            raise AttributeError("Missing 'file_path' attribute. Cannot save data unless import data filepath is available.")

        # Set for save_path based on availability
        # 1. Try get value from  save_path from 'savepath' 
        #       If savepath=None or "", try get value from getattr(self, "save_path", None)
        # 2. Try get value form getattr() 
        #       If form getattr() is None (default because attribute doesn't exist or is None), generate new savepath 
        # 3. If all else fails, generate save_path based on input file_path
        self.save_path = savepath or getattr(self, "save_path", None) or self._gen_savepath_from_filepath()
        saver = self.save_path

        [
        # if not hasattr(self, "save_path") and not self.save_path:
        #     # No self.save_path
        #     if not savepath:
        #         self.save_path = savepath # Update self.save_path based on provided savepath
        #     else:
        #         self.save_path = self._gen_savepath_from_filepath() # Update self.save_path based on stored self.filepath
        # save = self.save_path


        # Update save path based on availability
        # if not hasattr(self, "save_path") or not self.save_path:
        #         self.save_path = self._gen_savepath_from_filepath()
        # saver = self.save_path
        ]

        # Check output DataFrame availability 
        if not hasattr(self, "df_output"):
            raise AttributeError(
                "Missing 'df_output' attribute. Cannot save data unless data is imported and processed with 'load_dataframe' and 'process_data' method."
            )
        
        # Get output pd.DataFrame and save
        df = self.df_output        
        df.to_csv(saver, index=False)


    def load_and_process(self, filepath: str) -> pd.DataFrame:
        """The main method to run the partial handler workflow i.e. Load and Process Data."""

        # Assign input variables to appropriate class attributes
        self.file_path = filepath 

        self.load_dataframe()

        self.process_data()

        df = self.df_output

        return df


    def load_process_save(self, filepath: str, savepath: str|None = None):
        """The main method to run the complete handler workflow."""

        # Assign input variables to appropriate class attributes
        self.file_path = filepath 

        # If supplied savepath isn't available, save based on datetime name
        if not savepath:
            savepath = self._gen_savepath_from_filepath()
        self.save_path = savepath 

        self.load_dataframe()


        self.process_data()

        self.save_data()


if __name__ == "__main__":

    appointment_handler = BirthdayHandler()


    #! --------------------------
    #! DATA OUTPUT EXPECTATIONS
    #! --------------------------
    # Number: 27832319744
    # Name: Daniel Wilcox
    # Practice: CE PV (next door to Pick 'n Pay)
    #! --------------------------




