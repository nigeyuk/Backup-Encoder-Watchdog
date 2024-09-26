# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
ENABLE_DB_LOGGING = os.getenv('ENABLE_DB_LOGGING', 'True') == 'True'
CPU_LOAD_THRESHOLD = float(os.getenv('CPU_LOAD_THRESHOLD', 20.0))
OLD_FILE_THRESHOLD = int(os.getenv('OLD_FILE_THRESHOLD', 900))  # Default to 15 minutes
WAIT_TIME_BEFORE_BACKUP = int(os.getenv('WAIT_TIME_BEFORE_BACKUP', 300))  # Default to 5 minutes
ENABLE_DISCORD_UPDATES = os.getenv('ENABLE_DISCORD_UPDATES', 'True') == 'True'
DISCORD_UPDATE_INTERVAL = int(os.getenv('DISCORD_UPDATE_INTERVAL', 300))  # Default is 5 minutes
MAX_TS_FILES = int(os.getenv('MAX_TS_FILES', 10))  # Default to 10 if not specified

# Handle EXCLUDE_FILES, ensuring it defaults to an empty list if left blank
EXCLUDE_FILES = os.getenv('EXCLUDE_FILES', '')
if EXCLUDE_FILES:
    EXCLUDE_FILES = EXCLUDE_FILES.split(',')
else:
    EXCLUDE_FILES = []

# Configuration variables for services
ICECAST_URL = os.getenv('ICECAST_URL')
ICECAST_USER = os.getenv('ICECAST_USER')
ICECAST_PASS = os.getenv('ICECAST_PASS')
HLS_DIRECTORY = os.getenv('HLS_DIRECTORY')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
AWS_BACKUP_INSTANCE_ID = os.getenv('AWS_BACKUP_INSTANCE_ID')

