from aiogram.dispatcher.filters.state import StatesGroup, State


class BuyProductState(StatesGroup):
    client_name = State()
    client_phone = State()
    client_geo = State()

