from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent

# Folder with .env file
ENV_DIR = ROOT_DIR

# Temp folder
TEMP_DIR = ROOT_DIR / 'temp'

# Telegram bot folder
BOT_DIR = ROOT_DIR / 'tgbot'

# File with bad words
BAD_WORDS_FILE = BOT_DIR / 'filters' / 'badwords.txt'

# Folder with output data
OUTPUT_DATA_DIR = ROOT_DIR / 'output_data'
