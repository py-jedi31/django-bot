import asyncio
import logging

import aioschedule
from aiogram import Dispatcher
from aiogram.utils import executor
from decouple import config

from create_bot import dp, loop
from handler import (handlers_welcome, handlers_polls, handlers_game, handlers_help, handlers_main)


"""Логирование"""
logging.basicConfig(level=logging.INFO)


async def set_commands(dispatcher: Dispatcher):
    """Функция регистрации команд бота, при его запуске.
    ______
    :param dispatcher.
    """
    # await dispatcher.bot.set_my_commands([
    #     BotCommand(command="/start", description="Для запуска бота воспользуйтесь порталом"),
    #     # BotCommand(command="/re", description="Рестарт"),
    # ])
    pass


@dp.async_task
async def scheduler():
    """Запуск вопросов каждый день в TIME_START_POLL"""
    aioschedule.every().monday.at(config("TIME_START_POLL")).do(handlers_polls.send_all_weekly_polls)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)


async def on_startup(dispatcher: Dispatcher):
    """Функция регистрации хэндлеров бота, при его запуске.
    ______
    :param dispatcher.
    """
    # await set_commands(dispatcher)
    await scheduler()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=loop,)# on_startup=on_startup)
