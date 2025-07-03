# handlers/cekdata.py
from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import get_last_30_days_data
from datetime import timezone, timedelta

# Fungsi format data
def format_data(entry):
    # Ubah timezone ke WIB (UTC+7)
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        f"\n📌 <b>Data Kunjungan Sales</b>\n"
        f"🗓️ <b>Tanggal/Waktu</b> : {time_str}\n"
        f"📁 <b>Kategori</b>       : {entry.get('kategori', '-')}\n"
        f"👤 <b>Nama Sales</b>     : {entry.get('sales_name', '-')}\n"
        f"🏢 <b>Nama POI</b>       : {entry.get('poi_name', '-')}\n"
        f"📍 <b>Alamat</b>         : {entry.get('address', '-')}\n"
        f"\n👥 <b>Nama Kontak</b>    : {entry.get('contact_name', '-')}\n"
        f"🧑‍💼 <b>Jabatan</b>       : {entry.get('contact_position', '-')}\n"
        f"📞 <b>No. HP</b>         : {entry.get('contact_phone', '-')}\n"
        f"\n🏬 <b>STO</b>            : {entry.get('sto', '-')}\n"
        f"🌐 <b>Langganan</b>      : {entry.get('berlangganan', '-')}\n"
        f"🔌 <b>Provider</b>       : {entry.get('provider', '-')}\n"
        f"💰 <b>Biaya Internet</b> : {entry.get('cost', '-')}\n"
        f"\n🎯 <b>Jenis Kegiatan</b> : {entry.get('kegiatan', '-')}\n"
        f"💬 <b>Feedback</b>       : {entry.get('feedback', '-')}\n"
        f"📝 <b>Info Tambahan</b>  : {entry.get('detail_info', '-')}\n"
        f"========================================\n"
    )

# Handler untuk /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_last_30_days_data()

    if not data:
        await update.message.reply_text("📭 Tidak ada data dalam 30 hari terakhir.")
        return

    message = "📊 <b>Data 30 Hari Terakhir</b> (maks 30 data):\n"
    for entry in data:
        message += format_data(entry)

    # Telegram maksimal 4096 karakter per pesan
    for i in range(0, len(message), 4000):
        await update.message.reply_text(message[i:i+4000], parse_mode="HTML")
