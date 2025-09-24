import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CREDS_FILE = os.getenv("CREDS_FILE")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
