from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram import Router
import asyncio
import os

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

bot = Bot(token=TELEGRAM_API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я ваш бот-уведомитель. Я буду сообщать вам, когда у вас появятся новые сообщения.")


@router.message(Command('notify'))
async def send_notification(message: types.Message):
    await message.reply("Это тестовое уведомление.")


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
