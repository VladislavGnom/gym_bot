from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


kb_select_gym = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Gym Sport"), KeyboardButton(text="S-Fitness")]],
    resize_keyboard=True
)

kb_yes_or_not = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)


async def get_kb_select_trainer(data):
    kb = InlineKeyboardBuilder()
    for d in data:
        kb.add(InlineKeyboardButton(text=d[0], callback_data=d[1]))
    
    return kb.adjust(1).as_markup()

