# utils/error_handling.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)

def log_error(error: Exception, context: str = ""):
    logging.error(f"Error in {context}: {error}", exc_info=True)

def log_info(message: str):
    logging.info(message)
  
