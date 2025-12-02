import logging
import sys
import os

def setup_logger(name=__name__, log_level=logging.INFO):
    """
    Sets up a logger with console and file handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Check if handlers already exist to avoid duplicate logs
    if logger.hasHandlers():
        return logger
        
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
