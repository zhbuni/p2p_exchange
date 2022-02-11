from aiogram import types
from aiogram.dispatcher import FSMContext
from states.admin_states import AdminStates
from states.sell_states import SellStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.users.start import send_welcome
from sqlalchemy import func, and_

from loader import dp, db, User, Token, Proposal, Payment, Currency


dict_of_payment = {'ЕРИП': 'erip', 'МТБанк': 'mtbank', 'Другой банк': 'other', 'На номер телефона': 'phone',
                   'Альфа Банк': 'alpha'}
list_of_currency = ['ЕРИП', 'Альфа Банк', 'МТБанк', 'Другой банк', 'На номер телефона']


@dp.message_handler(commands=['add_token'])
async def add_token(message: types.Message):
    await AdminStates.AddNewToken.set()
    await message.answer("Enter token's name")


@dp.message_handler(state=AdminStates.AddNewToken)
async def handle_add_token(message: types.Message, state: FSMContext):
    token = Token(token_type=message.text)
    db.session.add(token)
    db.session.commit()
    await state.finish()
    await message.answer(f'Token {message.text} successfully added')


@dp.message_handler(commands=['add_currency'])
async def add_currency(message: types.Message):
    await AdminStates.AddNewCurrency.set()
    await message.answer("Enter currency's title")


@dp.message_handler(state=AdminStates.AddNewCurrency)
async def handle_add_currency(message: types.Message, state: FSMContext):
    currency = Currency(type=message.text)
    db.session.add(currency)
    db.session.commit()
    await state.finish()
    await message.answer(f'Currency {message.text} successfully added')


@dp.message_handler(commands=['add_payment'])
async def add_payment(message: types.Message):
    await AdminStates.AddNewPayment.set()
    await message.answer("Enter payment's title. Example: Альфа банк|alpha")


@dp.message_handler(state=AdminStates.AddNewPayment)
async def handle_add_payment(message: types.Message, state: FSMContext):
    if len(message.text.split('|')) != 2:
        await message.answer('Wrong input')
        return
    russian_title, english_title = message.text.split('|')
    payment = Payment(russian_title=russian_title, english_title=english_title)
    db.session.add(payment)
    db.session.commit()
    await state.finish()
    await message.answer(f'Payment {message.text} successfully added')


@dp.callback_query_handler(lambda c: c.data == 'back_to_sell' or c.data == 'cancel', state='*')
async def back_to_entry_point(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()
    await state.finish()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Купить', callback_data='buy'),
                 InlineKeyboardButton('Продать', callback_data='sell'))
    keyboard.add(InlineKeyboardButton('Мои объявления на продажу', callback_data='my_proposals'))
    keyboard.add(InlineKeyboardButton('Мои объявления на покупку', callback_data='my_proposals_to_buy'))
    keyboard.add(InlineKeyboardButton('Обратиться в поддержку', callback_data='support'))

    message_text = 'Вас приветствует обменник токенов'

    await callback_data.message.answer(text=message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ('sell', 'back_to_main_menu', 'buy'), state='*')
async def sell_tokens_handler(callback_data: types.CallbackQuery, state: FSMContext):
    if callback_data.data != 'back_to_main_menu':
        await state.update_data(type=callback_data.data)

    await callback_data.answer()
    await callback_data.message.delete()

    db_query_of_tokens = db.session.query(Token).all()
    list_of_tokens = []
    data = await state.get_data()
    type_of_operation = data['type']
    if callback_data.data == 'back_to_main_menu':
        await state.finish()
    type_to_show = 'sell' if type_of_operation == 'buy' else 'buy'
    proposals = db.session.query(Proposal).filter(Proposal.proposal_type == type_to_show).all()
    dict_of_counts = {}
    for i in range(len(list(set(filter(lambda x: x.token_type, proposals))))):
        dict_of_counts[proposals[i].token_type] = len(list(filter(lambda x: x.token_type == proposals[i].token_type,
                                                                  proposals)))

    for el in db_query_of_tokens:
        amount = dict_of_counts[el.id] if el.id in dict_of_counts else 0
        if amount:
            list_of_tokens.append(InlineKeyboardButton(f'{el.token_type}({amount})',
                                                       callback_data=f'{el.token_type}TOKEN{type_of_operation}'))

    text_type = 'продать' if type_of_operation == 'sell' else "купить"
    text = f'Выберите токен, который хотите {text_type}'
    button_text = 'продаже' if type_of_operation == 'sell' else 'покупке'

    keyboard = generate_inline_keyboard(list_of_tokens)
    keyboard.add(InlineKeyboardButton(text=f'Создать объявление о {button_text}',
                                      callback_data=f'create_proposal_{type_of_operation}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_sell'))

    await callback_data.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'TOKEN' in c.data or c.data == 'back_to_token_choose_ready_proposal', state='*')
async def show_proposals(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()

    await SellStates.GeneralState.set()

    await callback_data.answer()
    if 'TOKEN' in callback_data.data:
        splitted_data = callback_data.data.split('TOKEN')
        type_of_operation = splitted_data[1]
        token_type = splitted_data[0]
        await state.update_data(type=type_of_operation)
        await state.update_data(token=token_type)
    else:
        data = await state.get_data()
        type_of_operation = data['type']
        token_type = data['token']

    type_to_show = 'sell' if type_of_operation == 'buy' else 'buy'
    proposals = db.session.query(Proposal).join(Token).filter(and_(Proposal.proposal_type == type_to_show,
                                                                   token_type == Token.token_type)).all()

    dict_of_counts = {}
    for i in range(len(proposals)):
        dict_of_counts[proposals[i].currency] = len(list(filter(lambda x: x.currency == proposals[i].currency, proposals)))

    currency_list = db.session.query(Currency).all()
    list_of_buttons = []
    for currency in currency_list:
        amount = dict_of_counts[currency.type] if currency.type in dict_of_counts else 0
        if amount:
            list_of_buttons.append(InlineKeyboardButton(f'{currency.type}({amount})',
                                                        callback_data=f'{currency.type}ready_proposal_currency'))

    keyboard = generate_inline_keyboard(list_of_buttons)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_main_menu'))

    text_type = 'продажи' if type_of_operation == 'sell' else "покупки"
    await callback_data.message.answer(text=f'Выберите валюту для {text_type} токена', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'ready_proposal_currency' in c.data, state=SellStates.GeneralState)
async def choice_of_payment(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()
    data = await state.get_data()
    token = data['token']
    currency = callback_data.data[:-23]
    proposals = db.session.query(Proposal).join(Token).filter(and_(Proposal.currency == currency, Token.token_type == token)).all()
    for el in proposals:
        print(el.payment_method, '___')
    list_of_buttons = []
    for el in proposals:
        button = InlineKeyboardButton(text=f'{el.price} | {el.currency} ({el.min_amount} - {el.max_amount})',
                                      callback_data=f'proposal_{el.id}')
        list_of_buttons.append(button)
        print(f'{el.price} | {el.currency} ({el.min_amount} - {el.max_amount})')
    keyboard = InlineKeyboardMarkup()
    for el in list_of_buttons:
        keyboard.add(el)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_token_choose_ready_proposal'))

    await callback_data.answer()
    await SellStates.ProposalsState.set()
    await callback_data.message.answer(text='Выберите объявление', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'proposal_' in c.data, state=SellStates.ProposalsState)
async def proposal_handler(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()

    prop_id = int(callback_data.data[9:])
    proposal = db.session.query(Proposal).filter(Proposal.id == prop_id).first()
    token = proposal.token.token_type
    price = proposal.price
    currency = proposal.currency
    min_amount = proposal.min_amount
    max_amount = proposal.max_amount
    payment = proposal.payment_method

    data = await state.get_data()
    operation = data['type']
    text = 'Покупка' if operation == 'sell' else 'Продажа'
    button = InlineKeyboardButton(text=text, callback_data=f'{operation}_{prop_id}')
    keyboard = InlineKeyboardMarkup().add(button)
    keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='back_to_sell'))
    await state.finish()
    await callback_data.message.answer(text=f'Объявление №{prop_id}\n\n{text} {token} за {currency}\n\n' + \
                                            f'Курс: 1 {token} = {price} {currency}\n\n' + \
                                            f'От {min_amount} {token} до {max_amount} {token}\n\n' + \
                                            f'Метод оплаты: {payment}', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'ready_proposal_payment' in c.data, state='*')
async def choice_of_ready_proposal(callback_data: types.CallbackQuery):
    await callback_data.message.delete()
    await callback_data.answer()
    await callback_data.message.answer(text='Список доступных объявлений:')


@dp.callback_query_handler(lambda c: c.data == 'back_to_creating_proposal' or 'create_proposal' in c.data,
                           state='*')
async def create_proposal_choice_of_token(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()
    if callback_data.data != 'back_to_creating_proposal':
        operation_type = callback_data.data.split('_')[2]
        await state.update_data(type=operation_type)
    else:
        data = await state.get_data()
        operation_type = data['type']
    db_query_of_tokens = db.session.query(Token).all()
    list_of_tokens = []
    for el in db_query_of_tokens:
        list_of_tokens.append(InlineKeyboardButton(f'{el.token_type}',
                                                   callback_data=f'{el.token_type}proposal_create_token'))

    keyboard = generate_inline_keyboard(list_of_tokens)
    text_operation = 'продать' if operation_type == 'sell' else 'купить'
    text = f'Выберите токен, который хотите {text_operation}'
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_main_menu'))
    await callback_data.answer()
    await SellStates.TokenState.set()
    await callback_data.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'proposal_create_token' in c.data or 'back_to_currency_choosing_sell' in c.data,
                           state='*')
async def create_proposal_choice_of_currency(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()

    token = callback_data.data[:-21]
    if callback_data != 'back_to_currency_choosing_sell':
        await state.update_data(token=token)

    currency_list = db.session.query(Currency).all()
    list_of_buttons = []
    for currency in currency_list:
        list_of_buttons.append(InlineKeyboardButton(f'{currency.type}',
                                                    callback_data=f'{currency.type}choice_of_currency_proposal_create'))

    keyboard = generate_inline_keyboard(list_of_buttons)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_creating_proposal'))

    await callback_data.answer()
    await SellStates.CurrencyState.set()
    await callback_data.message.answer(text='Выберите валюту', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'choice_of_currency_proposal_create' in c.data or c.data == 'back_from_payment',
                           state='*')
async def create_proposal_choice_of_payment(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.delete()

    global dict_of_payment
    currency = callback_data.data[:-34]
    if callback_data.data != 'back_from_payment':
        await state.update_data(currency=currency)

    list_of_buttons = []
    list_of_payment_methods = db.session.query(Payment).all()
    for payment_type in list_of_payment_methods:
        list_of_buttons.append(InlineKeyboardButton(f'{payment_type.russian_title}',
                                                    callback_data=f'{payment_type.english_title}'
                                                                  f'proposal_create_choice_of_payment'))

    keyboard = generate_inline_keyboard(list_of_buttons)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_currency_choosing_sell'))

    await callback_data.answer()
    await SellStates.PaymentState.set()
    await callback_data.message.answer(text='Выберите платежную систему', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'proposal_create_choice_of_payment' in c.data, state=SellStates.PaymentState)
async def create_proposal_enter_info(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.answer()
    await callback_data.message.delete()

    payment = callback_data.data[:-33]
    await state.update_data(payment=payment)
    await SellStates.InfoState.set()

    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_from_payment'))
    await callback_data.message.answer('Введите всю необходимую информацию:\n\nНомер карты/счета/телефона,' + \
                                       ' комментарий к платежу и т.д.', reply_markup=keyboard)


@dp.message_handler(state=SellStates.InfoState)
async def create_proposal_price_enter(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)
    await SellStates.PriceState.set()
    await message.answer('Введите стоимость')


@dp.message_handler(state=SellStates.PriceState)
async def create_proposal_range_enter(message: types.Message, state: FSMContext):
    text = message.text.lower().strip()
    if len(text.split()) != 1 or not text.isdigit():
        await message.answer('Введены неправильные данные')
        return

    await state.update_data(price=text)
    await SellStates.RangeState.set()
    await message.answer('Введите диапазон количества токенов, в формате:\n\n0-10, 1.1-5.5')


@dp.message_handler(state=SellStates.RangeState)
async def create_proposal_confirm(message: types.Message, state: FSMContext):
    text = message.text.lower().strip()
    splitted_text = text.split('-')
    if len(splitted_text) != 2:
        await message.answer('Введены неправильные данные')
        return
    else:
        if not (text.split('-')[0].isdigit() or text.split('-')[1].isdigit()):
            await message.answer('Введены неправильные данные')
            return
    await state.update_data(range=text)
    data = await state.get_data()

    token = data['token']
    currency = data['currency']
    range_left, range_right = data['range'].split('-')
    query = db.session.query(func.max(Proposal.id)).first()
    if not query[0]:
        query = [0]
    proposals = query[0] + 1
    price = data['price']
    operation = data['type']
    text_operation = 'Продажа' if operation == 'sell' else 'Покупка'
    text = f'Объявление №{proposals}\n\n\t{text_operation} {token} за {currency}\n\n\tКурс:1' + \
           f' {token} = {price} {currency}\n\n\tОт {range_left} {token} До {range_right} {token}'

    await message.answer(text)
    await SellStates.PublishState.set()

    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Опубликовать', callback_data='publish_proposal'))
    keyboard.add(InlineKeyboardButton(text='Отменить', callback_data='cancel_add_of_proposal'))
    await message.answer('Опубликовать объявление?', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: 'publish_proposal' in c.data, state=SellStates.PublishState)
async def publish_proposal(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.answer()
    await callback_data.message.delete()
    data = await state.get_data()
    token_type = data['token']
    price = data['price']
    currency = data['currency']
    min_amount, max_amount = map(int, data['range'].split('-'))
    proposal_type = data['type']
    payment = data['payment']
    info = data['info']

    user = db.session.query(User).filter(User.telegram_id == callback_data.from_user.id).first()
    token = db.session.query(Token).filter(token_type == Token.token_type).first()
    proposal = Proposal(token_type=token.id,
                        price=price,
                        min_amount=min_amount,
                        user_id=user.id,
                        max_amount=max_amount,
                        currency=currency,
                        proposal_type=proposal_type,
                        payment_method=payment,
                        info=info
                        )
    db.session.add(proposal)
    db.session.commit()
    await state.finish()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Купить', callback_data='buy'),
                 InlineKeyboardButton('Продать', callback_data='sell'))
    keyboard.add(InlineKeyboardButton('Мои объявления на продажу', callback_data='my_proposals'))
    keyboard.add(InlineKeyboardButton('Обратиться в поддержку', callback_data='support'))
    await callback_data.message.answer('Объявление опубликовано', reply_markup=keyboard)


async def buy_tokens_handler(message: types.Message):
    pass


async def technical_support(message: types.Message):
    pass


def generate_inline_keyboard(buttons):
    kb = InlineKeyboardMarkup()
    for i in range(0, len(buttons), 2):
        if i != len(buttons) - 1:
            kb.add(buttons[i], buttons[i + 1])
        else:
            kb.add(buttons[i])
    return kb


def generate_inline_buttons(*args):
    lst = []
    for el in args:
        button = InlineKeyboardButton(text=el, callback_data=el)
        lst.append(button)
    return lst