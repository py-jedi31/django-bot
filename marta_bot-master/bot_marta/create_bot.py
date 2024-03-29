import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.mongo import MongoStorage

# Импортируем файл settings.py, находящийся в этой папке
try:
    import settings
except ModuleNotFoundError:
    from bot_marta import settings

# Получение данных из базы данных
# storage = MemoryStorage()
storage = MongoStorage(host=settings.DATABASES["state"]["HOST"],
                       port=settings.DATABASES["state"]["PORT"],
                       db_name=settings.DATABASES["state"]["NAME"],
                       username=settings.DATABASES["state"]["USERNAME"],
                       password=settings.DATABASES["state"]["PASSWORD"]
                       )

# создание бота
bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot, storage=storage)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot_name = loop.run_until_complete(bot.get_me())['username']
