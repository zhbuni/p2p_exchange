from aiogram import types
from aiogram.dispatcher import FSMContext
from states.edit_proposals import EditProposalStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, db, User, Proposal
from sqlalchemy import and_


@dp.callback_query_handler(lambda c: 'my_proposals' in c.data)
async def my_proposals(callback_data: types.CallbackQuery):
    operation_type = 'sell' if 'buy' not in callback_data.data else 'buy'
    await callback_data.answer()
    proposals = db.session.query(Proposal).join(User).filter(and_(User.id == Proposal.user_id,
                                                                  Proposal.proposal_type == operation_type)).all()
    if not proposals:
        await callback_data.message.answer('У вас нет объявлений')
        return
    await callback_data.message.delete()
    for i, el in enumerate(proposals):
        print(el.proposal_type)
        token = el.token.token_type
        price = el.price
        currency = el.currency
        min_amount = el.min_amount
        max_amount = el.max_amount

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'delete_proposal|{el.id}'))
        keyboard.add(InlineKeyboardButton('Изменить лимиты', callback_data=f'change_range|{el.id}'))
        keyboard.add(InlineKeyboardButton('Изменить цену', callback_data=f'change_price|{el.id}'))
        keyboard.add(InlineKeyboardButton('Поделиться', callback_data=f'share_proposal|{el.id}'))
        sell_or_buy = 'Продажа' if operation_type == 'sell' else 'Покупка'
        await callback_data.message.answer(text=f'Объявление №{el.id}\n\n{sell_or_buy} {token} за {currency}\n\n' + \
                                                f'Курс: 1 {token} = {price} {currency}\n\n' + \
                                                f'От {min_amount} {token} до {max_amount} {token}',
                                           reply_markup=keyboard)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Главное меню', callback_data='back_to_sell'))
    await callback_data.message.answer('На главное меню', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.split('|')[0] == 'delete_proposal')
async def delete_proposal(callback_data: types.CallbackQuery):
    await callback_data.message.delete()
    proposal_id = int(callback_data.data.split('|')[1])
    proposal = db.session.query(Proposal).filter(Proposal.id == proposal_id).first()
    if proposal:
        db.session.delete(proposal)
        db.session.commit()
        await callback_data.message.answer(f'Объявление №{proposal_id + 1} успешно удалено')


@dp.callback_query_handler(lambda c: c.data.split('|')[0] == 'change_range')
async def enter_change_range(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.answer()

    proposal_id = int(callback_data.data.split('|')[1])
    await state.update_data(proposal_id=proposal_id)

    await EditProposalStates.ChangeRange.set()
    await callback_data.message.answer('Введите диапазон количества токенов, в формате:\n\n0-10, 1.1-5.5')


@dp.message_handler(state=EditProposalStates.ChangeRange)
async def change_range(message: types.Message, state: FSMContext):
    text = message.text.lower().strip()
    if len(text.split('-')) != 2 and (not text.split('-')[0].isdigit() or not text.split('-')[1].isdigit()):
        await message.answer('Введены неправильные данные')
        return
    data = await state.get_data()

    proposal_id = data['proposal_id']
    proposal = db.session.query(Proposal).filter(Proposal.id == proposal_id).first()
    if proposal:
        min_v, max_v = text.split('-')
        proposal.min_amount = min_v
        proposal.max_amount = max_v
        await state.finish()
        db.session.commit()
        await message.answer('Количество возможных к продаже токенов изменено')


@dp.callback_query_handler(lambda c: c.data.split('|')[0] == 'change_price')
async def enter_change_price(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.answer()
    await callback_data.message.delete()

    proposal_id = int(callback_data.data.split('|')[1])
    await state.update_data(proposal_id=proposal_id)

    await EditProposalStates.ChangePrice.set()
    await callback_data.message.answer('Введите цену одного токена')


@dp.message_handler(state=EditProposalStates.ChangePrice)
async def change_price(message: types.Message, state: FSMContext):
    text = message.text.lower().strip()
    if len(text.split()) != 1 or not text.isdigit():
        await message.answer('Введены неправильные данные')
        return
    data = await state.get_data()

    proposal_id = data['proposal_id']
    proposal = db.session.query(Proposal).filter(Proposal.id == proposal_id).first()
    if proposal:
        price = int(text)
        proposal.price = price
        await state.finish()
        db.session.commit()
        await message.answer('Цена за 1 токен изменена')
