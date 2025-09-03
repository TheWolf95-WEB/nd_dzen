import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ChatType
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from db import init_db, upsert_post
from rss import router as rss_router
from utils import MEDIA_DIR, make_title

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CHANNEL_IDS = [int(cid.strip()) for cid in os.getenv("CHANNEL_IDS", "").split(",")]

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

app = FastAPI()
app.include_router(rss_router)
app.mount("/media", StaticFiles(directory="media"), name="media")

@dp.channel_post(F.chat.type.in_({ChatType.CHANNEL}))
async def new_post(msg: Message):
    if msg.chat.id not in CHANNEL_IDS:
        return

    text = msg.html_text or msg.text or ""
    title = make_title(text)
    link = f"https://t.me/c/{str(msg.chat.id)[4:]}/{msg.message_id}"
    date_ts = int(msg.date.timestamp())
    lead_image = None

    if msg.photo:
        best = msg.photo[-1]
        filename = f"{msg.chat.id}_{msg.message_id}.jpg"
        path = MEDIA_DIR / filename
        await bot.download(best, destination=path)
        lead_image = f"{BASE_URL}/media/{filename}"

    content_parts = [f"<p>{text}</p>"]
    if lead_image:
        content_parts.append(f'<p><img src="{lead_image}" alt=""></p>')

    content_html = "\n".join(content_parts)

    await upsert_post(
        id=msg.message_id,
        channel_id=msg.chat.id,
        date_ts=date_ts,
        title=title,
        link=link,
        content_html=content_html,
        lead_image=lead_image
    )

async def start():
    await init_db()
    task_bot = asyncio.create_task(dp.start_polling(bot))
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    task_server = asyncio.create_task(server.serve())
    await asyncio.gather(task_bot, task_server)

if __name__ == "__main__":
    asyncio.run(start())
