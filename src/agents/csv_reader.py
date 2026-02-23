import pandas as pd
from src.utils.logger import logger

class CSVReader:  # FIXED: Removed 'Agent' to match your import statement
    """
    CSV Reader
    - Reads feedback CSV files
    - Validates required columns
    - Returns structured data (DataFrame)
    """

    REQUIRED_COLUMNS = ["feedback_id", "user_feedback"]

    def __init__(self, required_columns=None):
        if required_columns:
            self.REQUIRED_COLUMNS = required_columns

    def read_csv(self, file_path: str) -> pd.DataFrame:
        try:
            # Note: file_path can be a string path or a Streamlit UploadedFile object
            df = pd.read_csv(file_path)
            logger.info(f"CSVReader: Successfully loaded data with {len(df)} rows.")
            
            # Validate required columns
            missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                logger.error(f"CSVReader: Missing required columns {missing_cols}")
                raise ValueError(f"Missing required columns: {missing_cols}")

            return df
            
        except Exception as e:
            logger.error(f"CSVReader: Error processing CSV - {e}")
            raise ValueError(f"Error reading CSV file: {e}")