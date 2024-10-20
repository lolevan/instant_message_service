from celery import Celery
import os
from aiogram import Bot

celery_app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))


@celery_app.task
def notify_user(telegram_id: str, content: str):
    bot.send_message(telegram_id, content)
