import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
import yt_dlp

TOKEN = "8958391218:AAFS-O8T_ZFJwWXF-RwUmsr2HBqhdjVPBWg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text)
async def download_media(message: types.Message):
    query = message.text

    if query.startswith("/"):
        return

    await message.answer("🔍 Qidirilmoqda va yuklanmoqda, iltimos kuting...")

    # Havola yoki matn ekanligini aniqlaymiz
    if not query.startswith("http://") and not query.startswith("https://"):
        # Matn bo'lsa - YouTube'dan audio qidiramiz
        search_query = f"ytsearch1:{query}"
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
        is_audio = True
    else:
        # Havola bo'lsa (Instagram, TikTok, YouTube video) - videoni o'zini yuklaymiz
        search_query = query
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }
        is_audio = False

    try:
        loop = asyncio.get_event_loop()
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(search_query, download=True)

        info = await loop.run_in_executor(None, extract)
        if 'entries' in info:
            info = info['entries'][0]

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)

        if is_audio:
            media_filename = filename.rsplit('.', 1)[0] + '.mp3'
            media_file = FSInputFile(media_filename)
            await message.answer_audio(audio=media_file, caption=info.get('title', 'Musiqa'))
        else:
            media_filename = filename
            media_file = FSInputFile(media_filename)
            await message.answer_video(video=media_file, caption=info.get('title', 'Video'))

        if os.path.exists(media_filename):
            os.remove(media_filename)

    except Exception as e:
        await message.answer("❌ Havolani yuklab bo'lmadi. Havola ochiq ekanligiga ishonch hosil qiling.")
        print(f"Xatolik: {e}")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())