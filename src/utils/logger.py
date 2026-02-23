import logging
import os

# Create a logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# 1. Setup the configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"), # Writes to a file
        logging.StreamHandler()              # Writes to your terminal
    ]
)

# 2. Define the 'logger' variable (this is what is being imported)
logger = logging.getLogger("FeedbackSystem")