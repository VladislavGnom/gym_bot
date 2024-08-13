from aiogram import F, Router, html
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import kb_select_gym, kb_yes_or_not
from help_func import register_user


router = Router()


class Register(StatesGroup):
    full_name = State()
    age = State()
    select_gym = State()
    checking_data = State()



def func_checking_data(data):
    text = \
    f'''
Проверь свои данные!

Твоё ФИО: <b>{html.quote(data['full_name'])}</b>
Твой возраст: <b>{html.quote(data['age'])}</b>
Твой тренажёрный зал: <b>{html.quote(data['gym'])}</b>
    '''
    return text


def get_all_commands():
    text = \
    f'''
/start - <b>{html.quote("запуск бота")}</b>
/help - <b>{html.quote("помощь по боту")}</b>
/cancel - <b>{html.quote("выйти из текущего процесса")}</b>
/add_train - <b>{html.quote("добавить результаты тренировки")}</b>
/show_progress - <b>{html.quote("показать прогресс за месяц")}</b>
    '''

    return text


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.set_state(Register.full_name)
    await message.answer(
        text=f"Привет {message.from_user.full_name}! Пройди мини регистрацию:)"
    )
    await message.answer(
        text=f"Введи своё ФИО"
    )


@router.message(Command("cancel"))
async def command_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Ты вышел из текущего процесса",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Register.full_name)
async def process_get_full_name(message: Message, state: FSMContext):
    is_correct = True if len(message.text.split()) == 3 else False

    if is_correct:
        await state.update_data(full_name=message.text)
        await state.set_state(Register.age)
        await message.answer(
            text="Введи свой возраст"
        )
    else:
        await message.answer(
            text="Вы не правильно ввели ФИО! Повторите попытку"
        )


@router.message(Register.age)
async def process_get_age(message: Message, state: FSMContext):
    try:
        age = int((message.text).strip())
        is_correct = True if 0 < age < 120 else False

        if is_correct:
            await state.update_data(age=str(age))
            await state.set_state(Register.select_gym)
            await message.answer(
                text="Выбери свой тренажёрный зал",
                reply_markup=kb_select_gym
            )
        else:
            await message.answer(
                text="Ты ввёл не корректный возраст. Попробуй снова!"
            )
    except ValueError as error:
        await message.answer(
            text="Ты ввёл не число, попробуй снова!"
        )


@router.message(Register.select_gym, (F.text.casefold() == "gym sport") | (F.text.casefold() == "s-fitness"))
async def process_get_select_gym(message: Message, state: FSMContext):
    await state.update_data(gym=message.text, user_id=message.from_user.id)
    data = await state.get_data()
    await state.set_state(Register.checking_data)
    await message.answer(
        text=func_checking_data(data),
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        text="Всё ли верно?",
        reply_markup=kb_yes_or_not
    )


@router.message(Register.select_gym)
async def invalid_select_gym(message: Message):
    await message.answer(
        text="Выбери зал нажав кнопку на клавиатуре"
    )


@router.message(Register.checking_data, F.text.casefold() == "да")
async def process_checking_data(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    if register_user(data):
        await message.answer(
            text="Это очень хорошо:) Поздравляю ты успешно зарегистрирован!",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Ты уже регистрировался на платформе ранее!",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Register.checking_data, F.text.casefold() == "нет")
async def process_checking_data(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Register.full_name)
    await message.answer(
        text="Жалко:( Начни процесс сначала!",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text=f"Введи своё ФИО"
    )



@router.message(Register.checking_data)
async def invalid_checking_data(message: Message):
    await message.answer(
        text="Выбери ответ нажав на кнопку на клавиатуре"
    )


@router.message(Command("help"))
async def command_help_handler(message: Message):
    await message.answer(
        text=get_all_commands(),
        parse_mode=ParseMode.HTML
    )
