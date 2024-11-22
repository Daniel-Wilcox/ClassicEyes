from dataclasses import dataclass, field
import pandas as pd
from ._abstract_handler import AbstractHandler


### Constants and Defaults ###
#! TODO: ensure all known junk words are provided
CONTACT_TYPE_LIST = ["Home", "Cell", "Work", "Fax", "EMail"]


#? CAN_CHANGE: These are the headings of the final dataframe, free to changeAdd in the full list of Optometrists
DEFAULT_CHOSEN_HEADINGS = [
    "CellCountry", "Name", "Practice", "Birthday", "Age"
]
# "Name", "Title", "Birthday", "BirthYear", "Age", "Contact", "CountryCode", "CellCountry",  "Practice"


DEFAULT_VALID_FILE_TYPES= [
    ".xls", 
    ".xlsx"
]


@dataclass
class BirthdayHandler(AbstractHandler):

    # Initialize file attributes
    #! Overwrite expected attributes to be defined within child class
    valid_file_types: list[str] = field(default_factory = lambda: DEFAULT_VALID_FILE_TYPES)

    #* Initialize child class's additional default attributes defined
    find_contact_list: list[str] = field(default_factory = lambda: CONTACT_TYPE_LIST)
    default_headings_list: list[str] = field(default_factory = lambda: DEFAULT_CHOSEN_HEADINGS)

    #* ---------------------
    #* Transform data methods
    #* ---------------------

    @staticmethod
    def _get_valid_phone_indices(df: pd.DataFrame, contact_type: str = "Cell", expected_contact_types: list | None = None):
        
        if expected_contact_types and (contact_type not in expected_contact_types):
            raise ValueError(f"{contact_type = } is not found in expected contact types list: {expected_contact_types}")
            
        category_mask = (df["Contact_Type"] == contact_type)
        has_content_mask = df["Contact"].notna() & (df["Contact"] != "")
        valid_len_mask = df["Contact"].apply(lambda x: len(str(x)) >= 10) 
        valid_start_mask = df["Contact"].apply(lambda x: str(x).startswith("0")) #("082", "083", "084", "079", "076", "072", "071", "078", "060", "011", "021")
        not_zeros_mask =  (df["Contact"] != "0000000000")
        union_mask = category_mask & has_content_mask & valid_len_mask & valid_start_mask & not_zeros_mask

        # Filter rows that match the contact category and have a valid phone number
        valid_rows = df[union_mask]
        return valid_rows.index

    # @abstractmethod
    def _clean_data(self, df: pd.DataFrame | None = None):
        
        # Retrieve relevant dataframe and validate
        self.df_raw = self._validate_dataframe("df_raw", df)
        df_raw = self.df_raw.copy()

        #* Clean up Excel:
        # Remove all empty rows and drop last row (Page 1 of 1)
        data_rows_clean = df_raw.iloc[:-1].dropna(how='all').reset_index(drop=True)

        # Remove all non-useful header rows (first 4)
        data_rows_clean = data_rows_clean.iloc[4:].reset_index(drop=True)

        # Remove all empty columns
        data_rows_clean = data_rows_clean.dropna(axis=1, how='all')

        # Extract the potential column headings
        new_col_list = data_rows_clean.iloc[0:2, :].fillna("").apply(lambda x: "".join(x), axis = 0).tolist()


        # Validate with expected column names
        VALID_COLUMN_NAMES = ["Birthday", "Home Address", "Postal Address", "Work Address", "Contact No."]
        to_validate_list = [col for col in new_col_list if col]
        faulty_columns = [col for col in to_validate_list if col not in VALID_COLUMN_NAMES]

        # If empty then False
        if any(faulty_columns):
            raise ValueError(f"Unexpected column names: {', '.join(faulty_columns)}.")

        # Replace empty columns with new unique names and assign to dataframe.columns
        default_column_list = [f"col_{i+1}" for i in range(new_col_list.count(""))]
        filler_iter = iter(default_column_list)
        data_rows_clean.columns = [item if item != "" else next(filler_iter) for item in new_col_list]
       
        data_rows_clean = data_rows_clean.iloc[2:, :].reset_index(drop=True) 
        
        # Remove unnecessary columns
        data_rows_clean = data_rows_clean.drop(columns=["Postal Address", "Work Address"])

        # Rename columns 
        data_rows_clean = data_rows_clean.rename(
            columns={"Birthday":"Name","Contact No.":"Contact", "Home Address":"Title"})

        # Get 'Birthday' data by shifting 'Name' column
        data_rows_clean["Birthday"] = data_rows_clean.loc[:, "Name"].shift(-1)

        # Find column that contains 'ContactType'
        #! Subject to change: 
        #! df.ContactType.unique() # [nan, 'Home', 'Cell', 'Work', 'Fax', 'EMail']
        unknown_col_df = data_rows_clean.loc[:, default_column_list]
        contact_col = unknown_col_df.columns[unknown_col_df.isin(self.find_contact_list).any()].tolist()

        if len(contact_col) == 1:
            data_rows_clean = data_rows_clean.rename(columns={contact_col[0]:"Contact_Type"})
        else:
            raise ValueError(f"Too many columns with unknown headings contain the contact type keywords: {self.find_contact_list}")

        # Find users titled names in 'Name' column (prev. 'Birthday' column) #! Possibly move to feature creation 
        all_string_rows = data_rows_clean.loc[:, "Name"].apply(lambda x: isinstance(x, str) and x.replace(" ", "").isalpha())
        data_rows_clean.loc[~all_string_rows, "Name"] = float("nan")
        data_rows_clean["Name"] = data_rows_clean.loc[:, "Name"].str.title()
        data_rows_clean["Name"] = data_rows_clean.loc[:, "Name"].ffill()
        
        # Clean 'Birthday' column
        data_rows_clean.loc[~all_string_rows, "Birthday"] = float("nan")
        data_rows_clean["Birthday"] = data_rows_clean.loc[:, "Birthday"].ffill()

        # Clean 'Title' column
        data_rows_clean.loc[~all_string_rows, "Title"] = float("nan")
        data_rows_clean["Title"] = data_rows_clean.loc[:, "Title"].str.title()
        data_rows_clean["Title"] = data_rows_clean.loc[:, "Title"].ffill()

        valid_indices = self._get_valid_phone_indices(data_rows_clean, contact_type="Cell")

        df_clean = data_rows_clean.loc[valid_indices, :].drop_duplicates().reset_index(drop=True)
        self.df_clean = df_clean.copy()

        return df_clean

    # @abstractmethod
    def _add_features(self, df: pd.DataFrame | None = None):

        # Retrieve relevant dataframe and validate
        self.df_clean = self._validate_dataframe("df_clean", df)
        df = self.df_clean.copy()

        # Add practice information:
        practice_string = f"Classic Eyes {self.selected_practice}"
        df["Practice"] = practice_string

        # Add Birthdate and age related features
        now_year = int(pd.to_datetime('now').year)

        df["Birthday"] = pd.to_datetime(df.loc[:, "Birthday"], errors='coerce')
        df["BirthYear"] = df.Birthday.dt.year.astype(int)
        df["Age"] = now_year - df['BirthYear']

        # Add country code and modify contact information for user
        df["CountryCode"] = "27"
        df["CellCountry"] = df["CountryCode"] + df["Contact"].apply(lambda x: str(x[1:]))

        # Reorder Dataframe
        df = df.reindex(self.default_headings_list, axis = 1)

        self.df_clean = df
        return df


    # @abstractmethod
    def save_data(self, savepath: str|None = None):
        """Save the cleaned data to a new file in save_folder."""

        # Check for file_path availability
        if not hasattr(self, "file_path"):
            raise AttributeError("Missing 'file_path' attribute. Cannot save data unless import data filepath is available.")

        # Set for save_path based on availability
        self.save_path = savepath or getattr(self, "save_path", None) or self._get_savepath_from_filepath()
 
        # Check output DataFrame availability 
        if not hasattr(self, "df_output"):
            raise AttributeError("Missing 'df_output' attribute. Cannot save data unless data is provided.")
        
        # Get output pd.DataFrame and save
        self.df_output.to_csv(self.save_path, index=False)


if __name__ == "__main__":

    birthday_handler = BirthdayHandler()




