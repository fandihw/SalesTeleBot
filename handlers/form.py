# handlers/form.py

import os
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.mongodb import save_data

# ─────────────────────────────────────────────────────────────
# Mapping dinamis TELDA ke opsi STO
# ─────────────────────────────────────────────────────────────
telda_sto_map = {
    "Bangkalan": ["SPG", "KML", "ARB", "KPP", "BKL", "OMB", "BEA", "TBU"],
    "Gresik": ["CRM", "POG", "BPG", "DDS", "SDY", "KDE", "BWN", "GSK"],
    "Lamongan": ["SDD", "LMG", "BBA", "BDG"],
    "Pamekasan": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Tandes": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Ketintang": ["WRU", "IJK", "RKT", "TPO"],
    "Manyar": ["GBG", "MYR", "JGR", "MGO"],
    "Kanjeran": ["KPS", "PRK", "KBL", "KJR"]
}

# ─────────────────────────────────────────────────────────────
# Langkah-langkah pengisian form
# ─────────────────────────────────────────────────────────────
steps = [
    "kategori", "kkontak", "telda", "sto", "kegiatan", "poi_name", "address",
    "ekosistem", "contact_name", "contact_position", "contact_phone",
    "provider", "provider_detail", "cost", "feedback", "feedback_detail",
    "detail_info"
]

# ─────────────────────────────────────────────────────────────
# Pilihan tombol per step
# ─────────────────────────────────────────────────────────────
options = {
    "kategori": ["Visit Baru", "Follow Up"],
    "telda": list(telda_sto_map.keys()),
    "kegiatan": ["Door to Door", "Out Bond Call"],
    "ekosistem": ["Ruko", "Sekolah", "Hotel", "Multifinance", "Health", "Ekspedisi",
                  "Energi", "Agriculture", "Properti", "Manufaktur", "Media & Communication"],
    "provider": ["Telkom Group", "Kompetitor", "Belum Berlangganan Internet"],
    "provider_detail_telkom": ["Indihome", "Indibiz", "Wifi.id", "Astinet", "Other"],
    "provider_detail_kompetitor": ["MyRep", "Biznet", "FirtsMedia", "Iconnet", "XL Smart",
                                   "Indosat MNCPlay", "IFORTE", "Hypernet", "CBN", "Fibernet", "Fiberstar", "Other"],
    "feedback": ["Bertemu dengan PIC/Owner/Manajemen", "Tidak bertemu dengan PIC"],
    "feedback_detail_ya": ["Tertarik Berlangganan Indibiz", "Tidak Tertarik Berlangganan Indibiz",
                           "Ragu-ragu atau masih dipertimbangkan"],
    "feedback_detail_tidak": ["Mendapatkan Kontak Owner/PIC/Manajemen", "Tidak Mendapatkan Kontak Owner/PIC/Manajemen"]
}

# ─────────────────────────────────────────────────────────────
# Label untuk setiap input
# ─────────────────────────────────────────────────────────────
labels = {
    "kategori": "Kategori",
    "kkontak": "KKONTAK",
    "telda": "TELDA",
    "sto": "STO",
    "kegiatan": "Jenis Kegiatan",
    "poi_name": "Nama POI",
    "address": "Alamat",
    "ekosistem": "Ekosistem",
    "contact_name": "Nama PIC",
    "contact_position": "Jabatan PIC",
    "contact_phone": "Telepon PIC",
    "provider": "Provider",
    "provider_detail": "Jenis Provider",
    "cost": "Abonemen Berlangganan",
    "feedback": "Feedback",
    "feedback_detail": "Detail Feedback",
    "detail_info": "Informasi Tambahan"
}


# ─────────────────────────────────────────────────────────────
# Handler untuk input tombol (inline keyboard)
# ─────────────────────────────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    step = context.user_data.get("step")
    selected_value = query.data
    context.user_data[step] = selected_value

    await query.edit_message_text(f"✅ Anda memilih: *{selected_value}*", parse_mode="Markdown")

    if step == "telda":
        context.user_data["step"] = "sto"
        keyboard = [[InlineKeyboardButton(sto, callback_data=sto)] for sto in telda_sto_map[selected_value]]
        await query.message.reply_text(
            f"Anda memilih {selected_value.title()}, pilih STO:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif step == "provider":
        if selected_value == "Belum Berlangganan Internet":
            context.user_data["provider_detail"] = "-"
            context.user_data["cost"] = "-"
            context.user_data["step"] = "feedback"
            await query.message.reply_text("ℹ️ Karena belum berlangganan, data provider & biaya dilewati.")
            await ask_next(update, context)
            return
        else:
            context.user_data["step"] = "provider_detail"
            detail_key = "provider_detail_telkom" if selected_value == "Telkom Group" else "provider_detail_kompetitor"
            keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[detail_key]]
            await query.message.reply_text("Pilih jenis provider:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

    elif step == "provider_detail" and selected_value == "Other":
        await query.message.reply_text("Masukkan nama provider lainnya:")
        return

    elif step == "feedback":
        context.user_data["step"] = "feedback_detail"
        detail_key = "feedback_detail_ya" if selected_value.startswith("Bertemu") else "feedback_detail_tidak"
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[detail_key]]
        await query.message.reply_text("Pilih detail feedback:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    next_index = steps.index(step) + 1
    if next_index < len(steps):
        context.user_data["step"] = steps[next_index]
        await ask_next(update, context)
    else:
        await query.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")


# ─────────────────────────────────────────────────────────────
# Handler untuk input teks
# ─────────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step not in steps:
        await update.message.reply_text("Terjadi kesalahan. /start untuk ulang.")
        return

    context.user_data[step] = update.message.text
    await update.message.reply_text(f"✅ Anda mengisi: *{update.message.text}*", parse_mode="Markdown")

    next_index = steps.index(step) + 1
    if next_index < len(steps):
        context.user_data["step"] = steps[next_index]
        await ask_next(update, context)
    else:
        await update.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")


# ─────────────────────────────────────────────────────────────
# Menampilkan pertanyaan berikutnya
# ─────────────────────────────────────────────────────────────
async def ask_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    label = labels.get(step, step.replace("_", " ").title())
    msg = update.effective_message

    if step in options:
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[step]]
        await msg.reply_text(f"Pilih {label}:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(f"Masukkan {label}:")


# ─────────────────────────────────────────────────────────────
# Handler foto (eviden) & simpan ke database + upload GDrive
# ─────────────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from services.drive import upload_photo  # Import lokal agar aman

    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    drive_url = upload_photo(file_path)

    # Gunakan timezone WIB
    wib = timezone(timedelta(hours=7))
    data = context.user_data.copy()
    data["photo_url"] = drive_url
    data["timestamp"] = datetime.now(wib)

    save_data(data)
    await update.message.reply_text("✅ Data dan eviden berhasil dikirim. Terima kasih!")
