"""Сделать рассылку с возможностью добавить кнопку и картинку"""
from aiogram import Bot, Dispatcher, types, executor
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from MARCUPS import get_ikb
from aiogram.dispatcher.filters.state import StatesGroup, State
import sql_for_rassilka
from config import TOKEN, MY_ID


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


# Состояния
class FSMAdmin(StatesGroup):
    photo = State()


class FSMAdmin_Text(StatesGroup):
    text = State()


class FSMAdminPhoto_and_Text(StatesGroup):
    photo = State()
    text = State()


class FSMAdminButton_and_Text(StatesGroup):
    button_url = State()
    button_text = State()
    text = State()


# При старте бота подключать бд и оповещать об этом
async def on_startup(_):
    await sql_for_rassilka.db_conn()
    print(f'{"..." * 8}\nReady! The database is connected and the bot is running')


# Добавляем новых пользователей в бд
@dp.message_handler(content_types=["new_chat_members"])
async def new_user(message: types.Message):
    await sql_for_rassilka.new_user(user_id=message.from_user.id)


@dp.message_handler(commands=['start'], state=None)
async def send_all(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Это бот админ!!!')
    await sql_for_rassilka.new_user(user_id=message.from_user.id)


@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cansel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == MY_ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


# Рассылка текста
@dp.message_handler(commands=['sendall_text'], state=None)
async def send_all(message: types.Message):
    if message.chat.id == MY_ID:
        await FSMAdmin_Text.text.set()
        await message.reply('Отправь мне текст или напиши /отмена')


@dp.message_handler(state=FSMAdmin_Text.text)
async def load_photo(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['text'] = message.text

        users = await sql_for_rassilka.all_user()
        await message.answer("Start")
        print(users)  # Нам дадут список с КОРТЕЖЕМ внутри!!!!!!!
        for i in users:
            print(i)
            await bot.send_message(*i, data['text'])

        await state.finish()


# Рассылка фото
@dp.message_handler(commands=['sendall_photo'], state=None)
async def cm_start(message: types.Message):
    if message.chat.id == MY_ID:
        await FSMAdmin.photo.set()
        await message.reply("Загрузи фото")


@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id

        users = await sql_for_rassilka.all_user()
        await message.answer("Start")
        print(users)  # Нам дадут список с КОРТЕЖЕМ внутри!!!!!!!
        for i in users:
            print(i)
            await bot.send_photo(*i, data['photo'])

        await state.finish()


# Рассылка фото и текста
@dp.message_handler(commands=['sendall_photo_text'], state=None)
async def cm_start(message: types.Message):
    if message.chat.id == MY_ID:
        await FSMAdminPhoto_and_Text.photo.set()
        await message.reply("Загрузи фото")


@dp.message_handler(content_types=['photo'], state=FSMAdminPhoto_and_Text.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
    await FSMAdminPhoto_and_Text.next()
    await message.answer(' Идём дальше! Скинь текст. ')


@dp.message_handler(state=FSMAdminPhoto_and_Text.text)
async def load_text(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['text'] = message.text

    users = await sql_for_rassilka.all_user()
    await message.answer("Start")
    print(users)  # Нам дадут список с КОРТЕЖЕМ внутри!!!!!!!
    for i in users:
        print(i)
        await bot.send_photo(*i, photo=data['photo'], caption=data['text'])

    await state.finish()


@dp.message_handler(commands=['sendall_text_button'], state=None)
async def send_all(message: types.Message):
    if message.chat.id == MY_ID:
        await FSMAdminButton_and_Text.button_url.set()
        await message.reply('Отправь мне URL ДЛЯ КНОПКИ или отправь /отмена')


@dp.message_handler(state=FSMAdminButton_and_Text.button_url)
async def load_button(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['button_url'] = message.text
        await FSMAdminButton_and_Text.next()
        await message.answer('Дальше текст на кнопке!')


@dp.message_handler(state=FSMAdminButton_and_Text.button_text)
async def load_button(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['button_text'] = message.text
        await FSMAdminButton_and_Text.next()
        await message.answer('Дальше текст сообщения.')


@dp.message_handler(state=FSMAdminButton_and_Text.text)
async def load_button(message: types.Message, state: FSMContext):
    if message.chat.id == MY_ID:
        async with state.proxy() as data:
            data['text'] = message.text

        users = await sql_for_rassilka.all_user()
        await message.answer("Start")
        print(users)  # Нам дадут список с КОРТЕЖЕМ внутри!!!!!!!
        for i in users:
            print(i)
            await bot.send_message(*i, data['text'],
                                   reply_markup=get_ikb(url=data['button_url'], text=data['button_text']))
        await message.answer('Готово!')
        await state.finish()


# Этот хендлер принимает в себя всё то что не прошло хендлеры выше
@dp.message_handler()
async def bot_not_know(message: types.Message):
    await bot.send_message(message.from_user.id, "Чел ты чё несёшь!?")


# Точка входа с запуском бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)