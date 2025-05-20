from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app
from strings.filters import command
from config import OWNER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


@app.on_message(
    command(["السورس", "سورس", "المبرمج"])
)
async def mak(client: Client, message: Message):
    await message.reply_photo(
        photo="https://envs.sh/Zow.jpg",
        caption="~ Team Al-Moussawi \n~ Dav Source",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⦗ Dev ⦘", url="https://t.me/YlYYU"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⦗ Updates ⦘", url="https://t.me/UUU10K"
                    ),
                    InlineKeyboardButton(
                        "⦗ support ⦘", url="https://t.me/PT_XV"
                    ),
                ],
            ]
        ),
    )
