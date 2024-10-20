from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import uvicorn
from app.routers import user, message
from app.tasks import celery_app
import app.utils as utils
from telegram_bot.bot import main as start_bot
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions to execute when starting up
    bot_task = asyncio.create_task(start_bot())
    yield
    # Actions to execute when shutting down
    bot_task.cancel()
    await bot_task

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=utils.SECRET_KEY)

app.include_router(user.router)
app.include_router(message.router)

# Web Interface Placeholder
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
