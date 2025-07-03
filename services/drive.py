import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from config import DRIVE_FOLDER_ID

def _authorize():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

_drive = _authorize()

def upload_photo(file_path: str) -> str:
    file_meta = {
        "title": os.path.basename(file_path),
        "parents": [{"id": DRIVE_FOLDER_ID}],
    }
    gfile = _drive.CreateFile(file_meta)
    gfile.SetContentFile(file_path)
    gfile.Upload()
    return f"https://drive.google.com/uc?id={gfile['id']}"
