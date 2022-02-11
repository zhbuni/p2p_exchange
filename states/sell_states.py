from aiogram.dispatcher.filters.state import State, StatesGroup


class SellStates(StatesGroup):
    PaymentState = State()
    PriceState = State()
    RangeState = State()
    TokenState = State()
    CurrencyState = State()
    InfoState = State()
    PublishState = State()

    GeneralState = State()
    ProposalsState = State()
    MenuState = State()