from dataclasses import dataclass, field
import pandas as pd
from ._abstract_handler import AbstractHandler


### Constants and Defaults ###
#! TODO: ensure all known junk words are provided
CONTACT_TYPE_LIST = ["Home", "Cell", "Work", "Fax", "EMail"]


#? CAN_CHANGE: These are the headings of the final dataframe, free to changeAdd in the full list of Optometrists
DEFAULT_CHOSEN_HEADINGS = [
    "Name",
    "Title",
    "Birthday",
    "BirthYear",
    "Age",
    "Contact",
    "CountryCode",
    "CellCountry", 
    "Practice"
]

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
    def _get_valid_phone_indices(df:pd.DataFrame, contact_category:str = "Cell"):

        category_mask = (df["Contact_Type"] == contact_category)
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

        # Remove all non-useful header rows )first 4
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

        # Remove unnecessary columns #! Possibly move or remove
        data_rows_clean = data_rows_clean.drop(columns=["Postal Address", "Work Address"])

        # Duplicate and rename columns
        data_rows_clean["Name"] = data_rows_clean["Birthday"]
        data_rows_clean["Title"] = data_rows_clean["Home Address"]
        data_rows_clean = data_rows_clean.iloc[2:, :].rename(columns={"Contact No.":"Contact"}).reset_index(drop=True) 

        # Find column that contains ContactType
        #! Subject to change: 
        #!  df.ContactType.unique() # [nan, 'Home', 'Cell', 'Work', 'Fax', 'EMail']
        unknown_col_df = data_rows_clean.loc[:, default_column_list]
        contact_col = unknown_col_df.columns[unknown_col_df.isin(self.find_contact_list).any()].tolist()

        if len(contact_col) == 1:
            data_rows_clean = data_rows_clean.rename(columns={contact_col[0]:"Contact_Type"})
        else:
            raise ValueError(f"Too many columns with unknown names contain the contact type keywords: {self.find_contact_list}")

        # Find users in name column #! Possibly move to feature creation 
        all_string_rows = data_rows_clean.loc[:, "Name"].apply(lambda x: isinstance(x, str) and x.replace(" ", "").isalpha())
        user_row_index = all_string_rows.index[all_string_rows]#.to_list()
        data_rows_clean.loc[~all_string_rows, "Name"] = None
        data_rows_clean["Name"] = data_rows_clean["Name"].ffill().str.title()

        # Get User names and titles with index to row in data_rows_clean
        only_users_df = data_rows_clean.loc[user_row_index, ["Name", "Title"]].reset_index(drop=True).copy()

        # Get user birthday #! Possibly move to feature creation 
        birthday_row_index = user_row_index + 1
        now_year = int(pd.to_datetime('now').year)

        only_users_df["Birthday"] = pd.to_datetime(
            data_rows_clean.loc[birthday_row_index, "Birthday"].reset_index(drop=True), errors='coerce'
        )
        only_users_df["BirthYear"] = only_users_df.Birthday.dt.year.astype(int)
        only_users_df["Age"] = now_year - only_users_df['BirthYear']

        # Add contact information to user #! Possibly move to feature creation
        valid_indices = self._get_valid_phone_indices(data_rows_clean, contact_category="Cell")

        only_users_df = pd.merge(
            only_users_df, 
            data_rows_clean.loc[valid_indices, ["Name", "Contact"]], 
            on='Name', how='inner'
        ) 

        # Add country code and modify contact information for user #! Possibly move to feature creation
        only_users_df["CountryCode"] = "27"
        only_users_df["CellCountry"] = only_users_df["CountryCode"] + only_users_df["Contact"].apply(lambda x: str(x[1:]))
        only_users_df["Name"] = only_users_df.Name.str.title()
        only_users_df


        # Assign class attribute with resulting DataFrame
        self.df_clean = only_users_df

        return only_users_df

    # @abstractmethod
    def _add_features(self, df: pd.DataFrame | None = None):

        # Retrieve relevant dataframe and validate
        self.df_clean = self._validate_dataframe("df_clean", df)
        df = self.df_clean.copy()


        # Add country code column
        #! Change phone numbers to include country code
        #TODO Add new features here

        # Add practice information:
        practice_string = f"Classic Eyes {self.selected_practice}"
        df["Practice"] = practice_string

        self.df_clean = df
        return df

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
 
        # Check output DataFrame availability 
        if not hasattr(self, "df_output"):
            raise AttributeError("Missing 'df_output' attribute. Cannot save data unless data is provided.")
        
        # Get output pd.DataFrame and save
        self.df_output.to_csv(self.save_path, index=False)




if __name__ == "__main__":

    birthday_handler = BirthdayHandler()


    #! --------------------------
    #! DATA OUTPUT EXPECTATIONS
    #! --------------------------
    # Number: 27832319744
    # Name: Daniel Wilcox
    # Practice: CE PV (next door to Pick 'n Pay)
    #! --------------------------




