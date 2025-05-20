import os
import re
import aiohttp
import logging
import asyncio
import json
import config
import wget
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from strings.filters import command
from youtube_search import YoutubeSearch
from AnonXMusic import app

from config import YAFA_NAME, YAFA_CHANNEL, CHANNEL_SUDO, BOT_USERNAME

# زر الاشتراك الإجباري
force_btn = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text=f"{YAFA_NAME}", url=f"{YAFA_CHANNEL}")]]
)

# التحقق من الاشتراك في القناة
async def check_is_joined(message):
    try:
        userid = message.from_user.id
        status = await app.get_chat_member(CHANNEL_SUDO, userid)
        if status.status in ["kicked", "left"]:
            raise Exception("Not joined")
        return True
    except Exception:
        await message.reply(
            "**⚠️︙عذراً، عليك الانضمام الى قناة البوت أولاً :**",
            reply_markup=force_btn,
            disable_web_page_preview=True
        )
        return False

# إزالة الرموز من العنوان
def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title).replace(' ', '_')

# الحصول على ملف الكوكيز
def get_cookies_file():
    cookie_dir = "AnonXMusic/utils/cookies"
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    return os.path.join(cookie_dir, cookies_files[0]) if cookies_files else None

# تحميل الصوت والصورة عبر yt_dlp
def download_audio_and_thumbnail(link, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        filename = ydl.prepare_filename(info)
        ydl.process_info(info)
        thumb_url = info.get("thumbnail")
        thumb_file = wget.download(thumb_url) if thumb_url else None
    return filename, thumb_file, info.get("title"), info.get("channel")

# الأمر الرئيسي
# ... الكود بدون تغيير حتى دالة song ...

@app.on_message(command(["song", "بحث", "تحميل", "تنزيل", "يوت", "yt"]) & (filters.private | filters.group | filters.channel))
async def song(client, message):
    if not await check_is_joined(message):
        return

    query = " ".join(message.command[1:])
    m = await message.reply("⦗ جارٍ التحميل ... ⦘")

    try:
        # المحاولة أولاً عبر yt_dlp باستخدام الكوكيز
        await m.edit("⦗ yt-dlp ... ⦘")

        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "cookiefile": get_cookies_file()
        }

        if "youtube.com" in query or "youtu.be" in query:
            link = query
        else:
            results = YoutubeSearch(query, max_results=1).to_dict()
            link = f"https://youtube.com{results[0]['url_suffix']}"

        loop = asyncio.get_event_loop()
        audio_file, thumb_file, title, performer = await loop.run_in_executor(
            None, download_audio_and_thumbnail, link, ydl_opts
        )

        caption = f"تم التحميل بواسطة @{BOT_USERNAME}" if BOT_USERNAME else "تم التحميل"
        await message.reply_audio(
            audio=audio_file,
            caption=caption,
            performer=performer or "YouTube",
            title=title,
            thumb=thumb_file,
        )
        await m.delete()
        os.remove(audio_file)
        if thumb_file:
            os.remove(thumb_file)

    except Exception as e:
        await m.edit("⦗ API ... ⦘")
        logging.error(f"yt_dlp fallback error: {str(e)}")

        try:
            api_url = "http://46.250.243.87:1470/youtube"
            api_key = "1a873582a7c83342f961cx0a177b2b26"
            params = {"query": query, "video": "false", "api_key": api_key}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API returned status code: {resp.status}")

                    text = await resp.text()
                    try:
                        data = json.loads(text)
                    except Exception:
                        raise Exception(f"فشل في قراءة JSON: {text[:200]}")

            stream_url = data.get("stream_url")
            title = data.get("title", "YouTube Audio")
            thumb_url = data.get("thumbnail")
            performer = data.get("channel", "YouTube")

            if not stream_url:
                raise Exception(f"stream_url غير موجود في البيانات: {data}")

            thumb_file = wget.download(thumb_url) if thumb_url else None
            filename = sanitize_filename(title) + ".m4a"

            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url) as response:
                    with open(filename, "wb") as f:
                        f.write(await response.read())

            caption = f"تم التحميل بواسطة @{BOT_USERNAME}" if BOT_USERNAME else "تم التحميل"
            await message.reply_audio(
                audio=filename,
                caption=caption,
                performer=performer,
                title=title,
                thumb=thumb_file,
            )
            await m.delete()
            os.remove(filename)
            if thumb_file:
                os.remove(thumb_file)

        except Exception as ee:
            await m.edit(f"❌ **خطأ:** {ee}")
            logging.error(f"API fallback error: {str(ee)}")
