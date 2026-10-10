import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import yt_dlp

# --- Render port talabini qondirish uchun veb-server ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Telegram Bot qismi ---
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. /start buyrug'i uchun alohida handler
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom! Men musiqa va video yuklab beruvchi botman.\n\n"
        "Menga quyidagilardan birini yuboring:\n"
        "🔗 YouTube yoki boshqa platforma havolasini\n"
        "📝 Qo'shiq nomini (masalan: *Sardor Rahimxon - Otam*)\n\n"
        "Men sizga tezda topib, audioni yuboraman! 🎵",
        parse_mode="Markdown"
    )

# 2. Ovozli xabarlar uchun
@dp.message(F.voice)
async def voice_handler(message: types.Message):
    await message.answer("🎙 Ovozli xabaringiz qabul qilindi. Hozircha qo'shiq nomini matn ko'rinishida yozib yuborishingizni so'rayman!")

# 3. Oddiy matn yoki havolalar uchun (Faqat /start dan boshqa matnlar)
@dp.message(F.text)
async def download_media(message: types.Message):
    query = message.text
    
    if query.startswith("/"):
        return

    await message.answer("🔍 Qidirilmoqda va yuklanmoqda, iltimos kuting...")
    
    if not query.startswith("http://") and not query.startswith("https://"):
        search_query = f"ytsearch1:{query} audio"
    else:
        search_query = query

   ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
}
    try:
        loop = asyncio.get_event_loop()
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(search_query, download=True)

        info = await loop.run_in_executor(None, extract)

        if 'entries' in info:
            info = info['entries'][0]

        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        
        title = info.get('title', 'Musiqa')

        if os.path.exists(mp3_filename):
            audio_file = types.FSInputFile(mp3_filename)
            await message.answer_audio(audio_file, caption=f"🎵 {title}")
            os.remove(mp3_filename)
        elif os.path.exists(filename):
            audio_file = types.FSInputFile(filename)
            await message.answer_audio(audio_file, caption=f"🎵 {title}")
            os.remove(filename)

    except Exception as e:
        await message.answer("❌ Qo'shiqni topib bo'lmadi yoki yuklashda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())