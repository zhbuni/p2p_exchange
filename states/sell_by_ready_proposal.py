from aiogram.dispatcher.filters.state import State, StatesGroup


class SellByProposalStates(StatesGroup):
    PaymentState = State()
    PriceState = State()
    RangeState = State()
    TokenState = State()
    CurrencyState = State()
    InfoState = State()
    PublishState = State()