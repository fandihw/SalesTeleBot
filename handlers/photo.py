from telegram import Update
from telegram.ext import ContextTypes
import os
from services.drive import upload_photo
from services.mongodb import save_data
from datetime import datetime, timedelta, timezone  

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()

    os.makedirs("photos", exist_ok=True) 

    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    # Upload ke Google Drive
    drive_url = upload_photo(file_path)

    # Simpan data ke MongoDB
    data = context.user_data.copy()
    data["photo_url"] = drive_url

    #Tambahkan timestamp WIB
    wib = timezone(timedelta(hours=7))
    data["timestamp"] = datetime.now(wib)

    save_data(data)

    await update.message.reply_text("✅ Data dan eviden berhasil dikirim. Terima kasih!")
