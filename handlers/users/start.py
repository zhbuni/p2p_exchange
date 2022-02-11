from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import dp, db, User


@dp.message_handler(commands=['me'])
async def get_me(message: types.Message):
    user = db.session.query(User).filter(User.telegram_id == message.from_user.id).first()
    await message.answer(f'You are {user.name} {user.surname}\nYour telegram id is {user.telegram_id}')


@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    user = db.session.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        user = User(name=f'{message.from_user.first_name}',
                    surname=f'{message.from_user.last_name}',
                    telegram_id=f'{message.from_user.id}')
        db.session.add(user)
        db.session.commit()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Купить', callback_data='buy'),
                 InlineKeyboardButton('Продать', callback_data='sell'))
    keyboard.add(InlineKeyboardButton('Мои объявления на продажу', callback_data='my_proposals'))
    keyboard.add(InlineKeyboardButton('Мои объявления на покупку', callback_data='my_proposals_to_buy'))
    keyboard.add(InlineKeyboardButton('Обратиться в поддержку', callback_data='support'))

    message_text = 'Вас приветствует обменник токенов'

    await message.answer(text=message_text, reply_markup=keyboard)


