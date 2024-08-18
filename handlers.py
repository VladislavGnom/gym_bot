from aiogram import F, Router, html
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from keyboards import kb_select_gym, kb_yes_or_not, get_kb_select_trainer
from help_func import register_user, get_trainers, save_result, output_data_trainers, exist_user


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

# ------------------------------------------------------------------

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

# ------------------------------------------------------------------

@router.message(Command("help"))
async def command_help_handler(message: Message):
    await message.answer(
        text=get_all_commands(),
        parse_mode=ParseMode.HTML
    )

# ------------------------------------------------------------------

class AddTrain(StatesGroup):
    select_simulator = State()
    max_weight = State()
    count_repeat = State()
    continue_or_not = State()
    finish_state = State()


@router.message(Command("add_train"))
async def command_add_train_handler(message: Message, state: FSMContext):
    if exist_user(message.from_user.id):
        await state.set_state(AddTrain.select_simulator)
        data = get_trainers(message)

        await message.answer(
            text="Выбери тренажёр для закрепления результата тренировки на нём:",
            reply_markup=await get_kb_select_trainer(data)
        )
    else:
        await message.answer(
            text="Ты ещё не зарегестрирован! Пожалуйста сделай это введя команду /start"
        )


@router.callback_query(F.data.startswith("trainer_"))
async def add_results_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(call_data=callback.data)
    await state.set_state(AddTrain.max_weight)
    await callback.answer("")
    await callback.message.answer(
        text="Твой максимально поднятый вес на тренажёре за сегодня(в кг)?"
    )


@router.message(AddTrain.max_weight)
async def process_get_max_weight(message: Message, state: FSMContext):
    try:
        numb = int((message.text).strip())
        if numb < 1:
            await message.answer("Введи корректный вес!")
        else:
            if numb > 150:
                await message.answer("Ух ты! Да ты силач, потрясающе!")

            await state.update_data(max_weight=str(numb), user_id=message.from_user.id)
            await state.set_state(AddTrain.count_repeat)
            await message.answer(
                text="Твоё количество повторений с этим весом?"
            )
    except ValueError as error:
        await message.answer(
            text="Вы ввели не число! Повторите попытку"
        )

    
@router.message(AddTrain.count_repeat)
async def process_get_count_repeat(message: Message, state: FSMContext):
    try:
        numb = int((message.text).strip())

        if numb < 1:
            await message.answer("Введи корректное количество повторений!")
        else:
            if numb > 150:
                await message.answer("Ух ты какой! Молодец, блестяще!")
                
            await state.update_data(count_repeat=str(numb))
            await state.set_state(AddTrain.continue_or_not)
            await message.answer(
                text="ОК, записал! Ты хочешь продолжить записывать результаты?",
                reply_markup=kb_yes_or_not
            )
    except ValueError as error:
        await message.answer(
            text="Вы ввели не число! Повторите попытку"
        )

@router.message(AddTrain.continue_or_not, F.text.casefold() == "да")
async def process_continue_or_not(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    if save_result(data):
        data = get_trainers(message)

        await state.set_state(AddTrain.select_simulator)
        await message.answer(
            text="ОК, Выбери тренажёр для закрепления результата тренировки на нём:",
            reply_markup=await get_kb_select_trainer(data)
        )
    else:
        await message.answer(
            text="Извини, произошла ошибка! Меня уже принялись чинить, поэтому ожидай",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(AddTrain.continue_or_not, F.text.casefold() == "нет")
async def process_continue_or_not(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    if save_result(data):
        await message.answer(
            text="ОК, записал твои результаты, будь ещё активней и достигай своих целей!",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Извини, произошла ошибка! Меня уже принялись чинить, поэтому ожидай",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(AddTrain.continue_or_not)
async def invalid_continue_or_not(message: Message):
    await message.answer(
        text="Ошибка! Нажми на кнопку на клавиатуре"
    )

# ------------------------------------------------------------------

@router.message(Command("show_progress"))
async def command_show_progress_handler(message: Message):
    await message.answer(
        text="Принял! Выполняю своё обязательство"
    )
    await show_calendar(message)


async def show_calendar(message: Message):
    calendar = SimpleCalendar()
    await message.answer(
        text="Выбери интересующий тебя день",
        reply_markup=await calendar.start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    
    if selected:
        data = output_data_trainers(callback.from_user.id, date.date())

        if data:
            await callback.message.answer(
                text=f"Твои упражнения сделанные в этот день({date.date()}): \n{data}",
                parse_mode=ParseMode.HTML
            )
        else:
            await callback.message.answer(
                text="<b>В этот день у тебя не было записанных тренировок</b>",
                parse_mode=ParseMode.HTML
            )
    else:
        ...

