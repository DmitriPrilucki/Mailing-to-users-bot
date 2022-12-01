from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_ikb(url, text):
    keyboard = InlineKeyboardMarkup(row_width=1)
    ib = InlineKeyboardButton(text=f'{text}', url=f'{url}')
    keyboard.add(ib)
    return keyboard