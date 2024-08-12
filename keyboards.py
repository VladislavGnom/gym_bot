from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


kb_select_gym = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Gym Sport"), KeyboardButton(text="S-Fitness")]],
    resize_keyboard=True
)

kb_yes_or_not = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

