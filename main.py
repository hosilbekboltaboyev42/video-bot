import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
import yt_dlp

TOKEN = "8958391218:AAFS-O8T_ZFJwWXF-RwUmsr2HBqhdjVPBWg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text.startswith("http"))
async def download_media(message: types.Message):
    await message.answer("⏳ Media yuklanmoqda, iltimos kuting...")
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = yt_dlp.YoutubeDL(ydl_opts).extract_info(message.text, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Media')

        video_file = types.FSInputFile(filename)
        await message.answer_video(video_file, caption=f"🎬 {title}")

        if os.path.exists(filename):
            os.remove(filename)
    except Exception:
        await message.answer("❌ Havoladan yuklab bo'lmadi yoki xatolik yuz berdi.")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())