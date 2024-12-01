from config import TOKEN, ID_ADMIN
from physics_error import SearchError, ValueNotUniqueError
from physics_scripts import PhysicsFormul, PhysicsName, AppendPhysicsFormuls
from utils.state_physics_formuls import StepGetPhysicsFormul, StepAppendPhysicsFormuls

from aiogram.types import Message
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


BOT_TOKEN = TOKEN
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command(commands=['start']))
async def process_start_command(message: Message) -> None:

    await message.answer('''Привет👋, Я Бот Роберт, который поможет тебе найти формулы по ✨физике✨.
У тебя наверняка возник вопрос, как пользоваться данным ботом 🤔?
Чтобы найти нужную формулу тебя надо написать комманду
/physics_formuls и ввести физическое обозначение, и бот тебе найдет все возможные формулы для нахождения этого обозначения, чтобы выйти из него напишите "cancel"
\nВот команды которые тебе могут пригодиться:\n
/tutorial_names - Все физические обозначения, которые я знаю🎓,
/physics_formuls - ищу формулу для этого физического обозначения🔍, \n/help - список всех комманд📋
/support - Поможем разобраться. Контакты админов.🔥

🔥(Для администрации)🔥

/append_formul - Добавление новых формул🖊️''')


@dp.message(Command(commands=['tutorial_names']))
async def process_tutorial_names_command(message: Message) -> None:

    physics_name_list = PhysicsName.get_all_physics_name()

    await message.answer('Вот все обозначения, которые может считывать наш бот:')

    for name_list in physics_name_list:

        await message.answer(f'\n{'·' + ',\n· '.join(name_list)}')


@dp.message(Command(commands=['help']))
async def process_help_command(message: Message) -> None:

    await message.answer('''Комманды которые я умею распозновать:
                         \n/tutorial_names - Все физические обозначения, которые я знаю🎓,
/physics_formuls - Ищу формулы для указонного физического обозначения🔍,
/help - команды которые знает📋
/support - Данные админов, чтобы связаться и решить ваши проблемы.🔥

🔥(Для администрации)🔥

/append_formul - Добавление новых формул🖊️''')


@dp.message(Command(commands=['physics_formuls']))
async def process_phisics_formuls(message: Message, state: FSMContext) -> None:  # Отлавливает комманду и выводит формулы которые нашёл

    await state.set_state(StepGetPhysicsFormul.GET_FORMULS)
    await message.answer('🔎Введите, пожалуйста, физическую величену, на которую хотите получить формулы🔍')
    await message.answer('Чтобы выйти из поиска нужно написать "cancel"✅')


@dp.message(StepGetPhysicsFormul.GET_FORMULS)
async def get_physics_formuls(message: Message, state: FSMContext) -> None:

    if message.text == 'cancel':

        await state.clear()
        await message.answer('Вы вышли из режима поиска формул✅')

        return None

    value = message.text.strip()

    if value:

        try:

            phisicsFormul = PhysicsFormul(value)

        except SearchError as error:

            await message.answer(str(error))

        else:

            await message.answer(f'''Вот все формулы, которые я смог найти в своей базе данных для {phisicsFormul.physics_name}:\n
Измеряется в {phisicsFormul.unit}\n
{'·' + ',\n· '.join(phisicsFormul.physics_formuls)}\n
Вот расшифровка всех формул в том же порядке: \n
{'·' + ',\n· '.join(phisicsFormul.physics_formuls_decoding)}''')

    else:

        await message.answer('❌Вы не ввели физическое обозначение❌')


@dp.message(Command(commands=['append_formul']))
async def process_append_formul(message: Message, state: FSMContext) -> None:

    if message.from_user.id not in ID_ADMIN:

        await message.answer('❌Извините, но у вас недостаточно прав для пользованием этой коммандой❌')

        return None

    await message.answer('Введите, пожалуйста, что ищёт ваша формула')
    await state.set_state(StepAppendPhysicsFormuls.VALUE)


@dp.message(StepAppendPhysicsFormuls.VALUE)
async def append_value_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(value=message.text)
    await message.answer('Отлично, теперь введите расшифровку физического обозначения')
    await state.set_state(StepAppendPhysicsFormuls.DESCRIPTION)


@dp.message(StepAppendPhysicsFormuls.DESCRIPTION)
async def appned_description_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(description=message.text)
    await message.answer('Хорошо, теперь введите саму формулу')
    await state.set_state(StepAppendPhysicsFormuls.FORMUL)


@dp.message(StepAppendPhysicsFormuls.FORMUL)
async def appned_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(formul=message.text)
    await message.answer('Превосходно, осталось совсем немного, введите в чём измеряется')
    await state.set_state(StepAppendPhysicsFormuls.UNIT)


@dp.message(StepAppendPhysicsFormuls.UNIT)
async def appned_unit_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(unit=message.text)

    data = await state.get_data()
    text = f'''Вы молодец. Вот что у нас с вами получилось:
\n·физическое обозначение: {data['value']},
·расшифровка: {data['description']},
·формула: {data['formul']},
·в чём измеряется: {data['unit']}'''

    await message.answer(text)
    await message.answer('''Всё верно ? \n(Напишите yes, если верно.\nНапишите no, если хотите попробовать ещё раз написать.
Напишите cancel, если хотите выйти из режима добавления формулы)''')
    await state.set_state(StepAppendPhysicsFormuls.ACCEPT)


@dp.message(StepAppendPhysicsFormuls.ACCEPT)
async def accept_formul(message: Message, state: FSMContext) -> None:

    if message.text == 'no':

        await state.clear()
        await message.answer('Введите, пожалуйста, что ищёт ваша формула')
        await state.set_state(StepAppendPhysicsFormuls.VALUE)

    elif message.text == 'cancel':

        await state.clear()
        await message.answer('Вы вышли из режима добавления формул')

    else:

        data = await state.get_data()
        try:

            append_physics_formul = AppendPhysicsFormuls(data['value'], data['description'], data['formul'], data['unit'])
            append_physics_formul.append_formul()

        except ValueNotUniqueError as error:

            await message.answer(str(error))

        await message.answer('Формула успешно добавлена')


@dp.message(Command(commands=['support']))
async def process_get_support(message: Message) -> None:

    await message.answer('''🔥Вот наши контакты:🔥
@Rodcooo,
@Id103628800.
Ответим в течение недели''')


@dp.message()
async def process_unknow_command(message: Message) -> None:

    await message.answer('''Извините неизвестная комманда, напишите комманду /help, чтобы узнать какие комманды поддерживает наш бот''')


if __name__ == '__main__':

    dp.run_polling(bot)
