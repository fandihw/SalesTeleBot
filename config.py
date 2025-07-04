from dotenv import load_dotenv
import os

load_dotenv()

# BOT
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "sales_visit_bot")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "visit_data")

# Google Drive
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")     # id folder drive
SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
