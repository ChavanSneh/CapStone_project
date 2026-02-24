import pandas as pd
from src.utils.logger import logger

class CSVReader:
    """
    CSV Reader
    - Reads feedback CSV files
    - Auto-generates IDs if missing
    - Maps column names intelligently for mobile compatibility
    """

    def __init__(self, required_columns=None):
        # We define what the agents NEED to function
        self.target_columns = ["feedback_id", "user_feedback"]

    def read_csv(self, file):
        try:
            df = pd.read_csv(file)
            
            # 1. Clean column names (removes hidden spaces or weird characters from mobile)
            df.columns = [c.strip().lower() for c in df.columns]

            # 2. Fix feedback_id: If missing, create a sequence
            if 'feedback_id' not in df.columns:
                logger.info("CSVReader: 'feedback_id' missing, auto-generating...")
                df['feedback_id'] = range(1, len(df) + 1)

            # 3. Fix user_feedback: Map common names to the one the Agent expects
            # Look for common names like 'feedback', 'text', 'comment', 'review'
            potential_text_cols = ['user_feedback', 'feedback', 'feedback_text', 'text', 'comments', 'review']
            
            found_text_col = None
            for col in potential_text_cols:
                if col in df.columns:
                    found_text_col = col
                    break
            
            if found_text_col and found_text_col != 'user_feedback':
                df = df.rename(columns={found_text_col: 'user_feedback'})
                logger.info(f"CSVReader: Renamed '{found_text_col}' to 'user_feedback'")
            
            # 4. Final Validation: Does 'user_feedback' exist now?
            if 'user_feedback' not in df.columns:
                raise ValueError("Could not find a feedback column. Please name your column 'user_feedback' or 'feedback'.")

            # 5. Return only what is needed (keeps the data clean for the agents)
            return df[['feedback_id', 'user_feedback']]

        except Exception as e:
            logger.error(f"CSVReader: Error processing CSV - {e}")
            raise ValueError(f"Error reading CSV file: {e}")