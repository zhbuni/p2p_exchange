from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):
    AddNewToken = State()
    AddNewCurrency = State()
    AddNewPayment = State()