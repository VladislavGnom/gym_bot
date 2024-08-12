from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import kb_select_gym, kb_yes_or_not


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

Твоё ФИО: {data['full_name']}
Твой возраст: {data['age']}
Твой тренажёрный зал: {data['gym']}
    '''
    return text



@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(Register.full_name)
    await message.answer(
        text=f"Привет {message.from_user.full_name}! Пройди мини регистрацию:)"
    )
    await message.answer(
        text=f"Введи своё ФИО"
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
            await state.update_data(age=age)
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
    await state.update_data(gym=message.text)
    data = await state.get_data()
    await state.set_state(Register.checking_data)
    await message.answer(
        text=func_checking_data(data)
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
    await state.clear()
    print(F.text.casefold())
    await message.answer(
        text="Это очень хорошо:) Поздравляю ты успешно зарегистрирован!",
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
        text="Выберите ответ нажав на кнопку на клавиатуре"
    )
