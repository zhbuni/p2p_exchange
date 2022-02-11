from aiogram.dispatcher.filters.state import State, StatesGroup


class EditProposalStates(StatesGroup):
    ChangeRange = State()
    ChangePrice = State()