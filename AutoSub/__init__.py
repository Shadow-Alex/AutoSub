# Package-level constant
VERSION = "1.0.0"

# Package-level configuration
CONFIG = {
    "debug": False,  # use smaller model and corpus when debug is set.
    "log_file": "log",
    "mode": "chat", # chat or completion
    "translation_path": 'translation',
    "transcription_path": 'transcription',
    "media_path": 'media',
    "out_path": 'out',
    "max_concurrent_req": 5,
}

DEBUG = CONFIG['debug']
MODE = CONFIG['mode']
translation_path = CONFIG['translation_path']
transcription_path = CONFIG['transcription_path']
media_path = CONFIG['media_path']
output_path = CONFIG['out_path']
max_concurrent_request = CONFIG['max_concurrent_req']

# Logging utils
import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler and set its level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a file handler and set its level
file_handler = logging.FileHandler(CONFIG['log_file'])
file_handler.setLevel(logging.DEBUG)

# Create a formatter and set its format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set the formatter for the handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)