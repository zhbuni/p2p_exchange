from aiogram import types
from aiogram.dispatcher import FSMContext
from states.sell_states import SellStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, db, User, Token, Proposal


@dp.callback_query_handler(lambda c: c.data == 'buy' or c.data == 'back_to_sell_menu')
async def buy_tokens(callback_data: types.CallbackQuery):
    await callback_data.answer()
    await callback_data.message.delete()
    db_query_of_tokens = db.session.query(Token).all()
    list_of_tokens = []
    proposals = db.session.query(Proposal).filter(Proposal.proposal_type == 'sell').all()

    dict_of_counts = {}
    for el in proposals:
        for el1 in proposals:
            if el1.token_type not in dict_of_counts:
                dict_of_counts[el1.token_type] = -1
            dict_of_counts[el1.token_type] += 1

    for el in db_query_of_tokens:
        amount = dict_of_counts[el.id] if el.id in dict_of_counts else 0
        list_of_tokens.append(InlineKeyboardButton(f'{el.token_type}({amount})',
                                                   callback_data=f'{el.token_type}BUYTOKEN'))

    keyboard = generate_inline_keyboard(list_of_tokens)
    keyboard.add(InlineKeyboardButton(text='Создать объявление о покупке', callback_data='create_buy_proposal'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_sell'))#back_to_create_buy_proposal
    text = 'Выберите токен, который хотите купить'
    await callback_data.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ('create_buy_proposal', 'back_to_creating_proposal_to_sell'))
async def create_proposal_to_buy_choose_token(callback_data: types.CallbackQuery):
    await callback_data.message.delete()
    db_query_of_tokens = db.session.query(Token).all()
    list_of_tokens = []
    for el in db_query_of_tokens:
        list_of_tokens.append(InlineKeyboardButton(f'{el.token_type}',
                                                   callback_data=f'{el.token_type}proposal_create_token_to_sell'))

    keyboard = generate_inline_keyboard(list_of_tokens)
    text = 'Выберите токен, который хотите купить'
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_sell_menu'))
    await callback_data.answer()
    await BuyTokenStates.TokenState.set()
    await callback_data.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'proposal_create_token_to_sell' in c.data, state='*')
async def create_proposal_to_sell_choice_of_currency(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()

    token = callback_data.data[:-29]
    await state.update_data(token=token)
    list_of_currency = ['USD', 'RUB', 'EUR', 'BYN', 'UAH', 'KZT']
    list_of_buttons = []
    for i in range(len(list_of_currency)):
        list_of_buttons.append(InlineKeyboardButton(f'{list_of_currency[i]}',
                                                    callback_data=f'{list_of_currency[i]}'
                                                                  f'choice_of_currency_proposal_create_to_sell'))

    keyboard = generate_inline_keyboard(list_of_buttons)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_creating_proposal_to_sell'))

    await callback_data.answer()
    await SellStates.CurrencyState.set()
    await callback_data.message.answer(text='Выберите валюту', reply_markup=keyboard)


def generate_inline_keyboard(buttons):
    kb = InlineKeyboardMarkup()
    for i in range(0, len(buttons), 2):
        if i != len(buttons) - 1:
            kb.add(buttons[i], buttons[i + 1])
        else:
            kb.add(buttons[i])
    return kb