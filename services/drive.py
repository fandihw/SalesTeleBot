import os
import json
from dotenv import load_dotenv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

load_dotenv()

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# Autentikasi dari .env (bukan file service_account.json lagi)
def authorize_drive():
    json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    info = json.loads(json_str)

    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    gauth = GoogleAuth()
    gauth.auth_method = 'service'
    gauth.credentials = credentials
    return GoogleDrive(gauth)

drive = authorize_drive()

def upload_photo(file_path):
    from os.path import basename

    gfile = drive.CreateFile({
        'title': basename(file_path),
        'parents': [{'id': DRIVE_FOLDER_ID}]
    })
    gfile.SetContentFile(file_path)
    gfile.Upload()
    return gfile['alternateLink']
