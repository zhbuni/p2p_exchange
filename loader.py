from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.db_api.db import Database
from utils.db_api.models.user import User
from utils.db_api.models.tokens import Token
from utils.db_api.models.proposals import Proposal
from utils.db_api.models.payment import Payment
from utils.db_api.models.currency import Currency
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()
