import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db
from check_traffic_job import check_traffic_job
from handlers import register_handlers

API_TOKEN = "ТУТ ТОКЕН"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()

async def on_startup(_):
    db.init_db()
    scheduler.add_job(check_traffic_job, 'interval', hours=48, args=[bot])
    scheduler.start()

if __name__ == "__main__":
    register_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup)
