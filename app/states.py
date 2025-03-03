from aiogram.fsm.state import State, StatesGroup


class Chat(StatesGroup):
    text = State()
    wait = State()


class ImageGenerator(StatesGroup):
    generate = State()
    wait = State()


class Newsletter(StatesGroup):
    message = State()
