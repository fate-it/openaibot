from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import app.keyboards as kb
from app.states import Chat, ImageGenerator
from aiogram.fsm.context import FSMContext
from app.generators import gpt_text, gpt_image, gpt_vision
from app.database.requests import set_user, get_user, calculate
from decimal import Decimal
import uuid
import os


user = Router()


@user.message(F.text == 'Отмена')
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer('Добро пожаловать!', reply_markup=kb.main)
    await state.clear()


@user.message(F.text == 'Генерация картинок')
async def image_generation(message: Message, state: FSMContext):
    tg_user = await get_user(message.from_user.id)
    if Decimal(tg_user.balance) > 0:
        await state.set_state(ImageGenerator.generate)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Не достаточно средств балансе.')


@user.message(ImageGenerator.generate)
async def generate_response(message: Message, state: FSMContext):
    tg_user = await get_user(message.from_user.id)
    if Decimal(tg_user.balance) > 0:
        await state.set_state(ImageGenerator.wait)
        response = await gpt_image(message.text, 'dall-e-3')
        await calculate(response['usage'], 'dall-e-3', tg_user)
        print(response)
        try:
            await message.answer_photo(photo=response['response'])
        except Exception as e:
            print(e)
            await message.answer(response['response'])
        await state.set_state(ImageGenerator.generate)
    else:
        await message.answer('Не достаточно средств балансе.')


# @user.message(ImageGenerator.wait)
# async def wait_wait(message: Message):
#     await message.answer('Ваша картинка генирируеться, подождите.')


@user.message(F.text == 'Чат')
async def chatting(message: Message, state: FSMContext):
    tg_user = await get_user(message.from_user.id)
    if Decimal(tg_user.balance) > 0:
        await state.set_state(Chat.text)
        await message.answer('Введите ваш запрос', reply_markup=kb.cancel)
    else:
        await message.answer('Не достаточно средств балансе.')


@user.message(Chat.text, F.photo)
async def chat_response(message: Message, state: FSMContext):
    tg_user = await get_user(message.from_user.id)
    if Decimal(tg_user.balance) > 0:
        await state.set_state(Chat.wait)
        file = await message.bot.get_file(message.photo[-1].file_id)
        file_path = file.file_path
        file_name = f'{uuid.uuid4()}.jpeg'
        await message.bot.download_file(file_path, file_name)
        response = await gpt_vision(message.caption, 'gpt-4o', file_name)
        await calculate(response['usage'], 'gpt-4o', tg_user)
        await message.answer(response['response'])
        await state.set_state(Chat.text)
        os.remove(file_name)
    else:
        await message.answer('Не достаточно средств балансе.')


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    tg_user = await get_user(message.from_user.id)
    if Decimal(tg_user.balance) > 0:
        await state.set_state(Chat.wait)
        response = await gpt_text(message.text, 'gpt-4o')
        await calculate(response['usage'], 'gpt-4o', tg_user)
        await message.answer(response['response'])
        await state.set_state(Chat.text)
    else:
        await message.answer('Не достаточно средств балансе.')


@user.message(ImageGenerator.wait)
@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.answer('Ваше сообщение генирируеться, подождите.')

