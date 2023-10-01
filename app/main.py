import logging

from aiogram import types
from fastapi import FastAPI

from app.api.api import api
from app.core.config import settings
from app.db.session import dispose_engine, get_or_create_engine
from app.logging import start_logging
from app.telegtam_bot.bot import Bot, Dispatcher, bot, dp

app = FastAPI(
    title="Name of service",
    description="Description of your service",
    version="Version of service",
)

WEBHOOK_PATH = f"/bot/{settings.TELEGRAM_API_TOKEN}"
WEBHOOK_URL = settings.WEBHOOK_URL + WEBHOOK_PATH


@app.on_event("startup")
async def startup():
    get_or_create_engine()
    start_logging()

    webhook_info = await bot.get_webhook_info()
    if webhook_info != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
    logging.info("Bot started")


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def shutdown():
    await bot.session.close()
    logging.info("Bot stopped")
    await dispose_engine()


app.include_router(api)
