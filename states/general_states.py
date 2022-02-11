from aiogram.dispatcher.filters.state import State, StatesGroup


class SellStates(StatesGroup):
    BuyState = State()
    SellState = State()
    MyProposalsState = State()
    SupportState = State()