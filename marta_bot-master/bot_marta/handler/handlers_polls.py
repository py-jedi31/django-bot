from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted, MessageNotModified
from loguru import logger

import async_db
import markup
import liters
from aiogram import types
from aiogram.dispatcher import FSMContext

from create_bot import dp, storage
from handler.handlers_welcome import call_main_menu, restart
from utils import BotState, POLL_STATE, CONNECT_POLL, create_pin_message, delete_main_message, call_main, \
    valid_parse_mode


@dp.callback_query_handler(
    lambda c: c.data in [kb_data[1] for kb_data in markup.HOW_LONG_KB],
    state=BotState.HOW_LONG_WORK,
)
async def how_long_work(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинает опрос в соответствии с выбранным вариантом ответа
    _____
    Кнопки:
    Срабатывание - "Менее двух недель", "2 - 6 недель", '6 - 12 недель', "Более 12 недель"
    Создает - 1 вопрос из POLL№ в соответствии с выбранным вариантом ответа на вопрос "Как долго работаешь?"
    _____
    Переходит в состояние POLL№.
    """
    await callback_query.answer()
    await state.update_data(how_long_work=callback_query.data)
    user_data = await state.get_data()
    if callback_query.data == "less_2":

        if not user_data["pin_message"]:
            mes = await create_pin_message(
                callback_query.message.chat.id, callback_query.message.message_id
            )

        else:
            await delete_main_message(callback_query.message.chat.id, callback_query.message.message_id)
            mes = user_data['pin_message']
        new_mes = await callback_query.bot.send_message(
            callback_query.message.chat.id,
            liters.NOT_TODAY + "\n\n" + liters.MAIN_MENU,
            reply_markup=markup.INLINE_KB_MAIN,
            )
        await async_db.insert_or_update_state(
            user_id=callback_query.from_user.id,
            pin_id=mes,
            main_id=new_mes.message_id,
            state="BotState:MAIN",
        )
        await state.set_state(BotState.MAIN)
        await state.update_data(
            first_message=new_mes.message_id, pin_message=mes
        )
    else:
        poll_id = CONNECT_POLL[callback_query.data]
        poll = await async_db.select_poll(poll_id=poll_id)
        question_id, poll_first_question, count_key, key_options, text_answer = poll[0]
        await callback_query.message.edit_text(
            liters.INSTRUCTION_POLL.format("")
            + "\n\n" +
            poll_first_question.capitalize(),
            reply_markup=markup.range_inline_kb(count_key, "p", key_options.split(";")),
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        await state.update_data(poll_question=0, poll=tuple(map(lambda x: tuple(x), poll)), poll_id=poll_id)
    await POLL_STATE[callback_query.data].set()


@dp.callback_query_handler(
    lambda c: c.data in map(lambda x: str(x) + "p", range(1, 6)),
    state=
    (
        BotState.POLL1,
        BotState.POLL2,
        BotState.POLL3,
        BotState.POLL_START,
        BotState.POLL_EVERYWEEK,
    ),
)
async def poll_func_kb(callback_query: types.CallbackQuery, state: FSMContext):
    """Записывает результат ответа на предыдущий вопрос в БД, выдает новый вопрос.
    Если Вопрос последний, то переводит в состояние MAIN.
     _____
    Кнопки:
    Срабатывание - Кнопки опросов (1, 2, 3 и т.д)
    Создает - Новый вопрос по списку.
    """
    await callback_query.answer()
    user_data = await state.get_data()
    await async_db.insert_answer(
        user_id=user_data["user_id"],
        question_id=user_data["poll"][user_data["poll_question"]][0],
        answer=callback_query.data.replace("p", ""),
    )
    await state.update_data(
        poll_question=user_data["poll_question"] + 1,
    )
    user_data = await state.get_data()

    try:
        question_id, question, count_key, key_options, text_answer = user_data["poll"][
            user_data["poll_question"]
        ]
        await callback_query.message.edit_text(
            question,
            reply_markup=markup.range_inline_kb(count_key, "p", key_options.split(";")),
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    except IndexError:
        await write_poll_answer(state)


@dp.message_handler(state=(
        BotState.POLL1,
        BotState.POLL2,
        BotState.POLL3,
        BotState.POLL_START,
        BotState.POLL_EVERYWEEK,
))
async def poll_func_ms(message: types.Message, state: FSMContext):
    """Записывает текст сообщения как ответ, если вопрос подразумевает ответ сообщением, если нет, то удаляет
    сообщение пользователя"""
    user_data = await state.get_data()
    try:
        question_id, question, count_key, key_options, text_answer = user_data[
            "poll"
        ][user_data["poll_question"]]

    except IndexError:
        question_id, question, count_key, key_options, text_answer = [None for x in range(5)]

    if text_answer:
        """
        Если у вопроса установлен флаг text_answer то пользователь сможет отвечать на вопрос текстом.
        Далее по скрипту идет запись ответа и выдача нового вопроса. ( или завершение скрипта, если был последний
        вопрос в опросе
        """

        await async_db.insert_answer(
            user_id=user_data["user_id"],
            question_id=question_id,
            answer=message.text,
        )
        await state.update_data(
            poll_question=user_data["poll_question"] + 1,
        )
        user_data = await state.get_data()
        try:
            """
            Получение информации о новом вопросе. Если выпадает в ошибку, то это был последний вопрос в опросе
            """
            question_id, question, count_key, key_options, text_answer = user_data[
                "poll"
            ][user_data["poll_question"]]

        except IndexError:
            """
            Создает мэин меню и записывает время окончания прохождения опроса
            """
            await write_poll_answer(state)
            await message.delete()

        try:
            await message.bot.edit_message_text(
                question,
                message.from_user.id,
                user_data["first_message"],
                reply_markup=markup.range_inline_kb(
                    count_key, "p", key_options.split(";")
                ),
                parse_mode=types.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        except MessageNotModified:
            await delete_main_message(message.from_user.id, main_id=user_data["first_message"])
            await message.answer(
                question,
                reply_markup=markup.range_inline_kb(
                    count_key, "p", key_options.split(";")
                ),
                parse_mode=types.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        await message.delete()
    else:
        """
        Если вопрос не содержит флага text_answer, то происходит проверка на команды бота
        """
        if message.text == '/re':
            await restart(message, state)
        elif message.text == '/start':
            if not user_data["pin_message"]:
                mes = await create_pin_message(
                    message.chat.id, message.message_id
                )
                await state.update_data(pin_message=mes)
            else:
                mes = user_data['pin_message']
                await delete_main_message(message.chat.id, user_data['first_message'])
            main_id = await call_main(message.chat.id)
            await async_db.insert_or_update_state(
                user_id=message.chat.id,
                main_id=main_id,
                pin_id=mes,
                state="BotState:MAIN",
            )
            pass
        else:

            await message.delete()


async def write_poll_answer(state: FSMContext):
    """
    Запись результатов опроса
    :param state:
    :return:
    """
    user_data = await state.get_data()
    await async_db.insert_poll_answer(
        user_id=user_data["user_id"], poll_id=user_data["poll_id"]
    )
    if not user_data["pin_message"]:
        mes = await create_pin_message(user_data["user_id"], user_data['first_message'])
    else:
        mes = user_data['pin_message']
        await delete_main_message(user_data["user_id"], user_data['first_message'])
    new_mes = await dp.bot.send_message(
        user_data["user_id"],
        text=liters.CONGRATULATION + "\n\n" + liters.MAIN_MENU,
        reply_markup=markup.INLINE_KB_MAIN,
    )

    await BotState.MAIN.set()
    if user_data['poll_id'] == 4:
        await async_db.insert_or_update_state(
            user_id=user_data["user_id"],
            main_id=new_mes.message_id,
            pin_id=mes,
            state="BotState:MAIN",
            has_init_poll=True
        )
    else:
        await async_db.insert_or_update_state(
            user_id=user_data["user_id"],
            main_id=new_mes.message_id,
            pin_id=mes,
            state="BotState:MAIN",
        )
    await state.update_data(
        first_message=new_mes.message_id, pin_message=mes
    )


async def call_weekly_polls(user_id,):
    """Начинает стартовый опрос
    _____
    Кнопки:
    Создает - 1 вопрос из POLL№ в соответствии с флагом init_poll пользователя
    _____
    Переходит в состояние POLL_*.
    """
    user = await async_db.select_state(
        user_id=user_id,
        with_init_poll=True
    )
    user_id, main_message, _, state_user, has_init_poll = user[0]
    poll_id, state_bot = (5, BotState.POLL_START) if has_init_poll else (4, BotState.POLL_EVERYWEEK)
    poll = await async_db.select_poll(poll_id=poll_id)
    question_id, poll_first_question, count_key, key_options, text_answer = poll[0]
    await delete_main_message(user_id, main_message)
    mes = await valid_parse_mode(
            dp.bot.send_message,
            user_id,
            liters.INSTRUCTION_POLL.format(liters.INTRODUCTION_FOR_WEEKLY_POLL[poll_id])
            + '\n\n' + poll_first_question.capitalize(),
            reply_markup=markup.range_inline_kb(count_key, "p", key_options.split(";")),
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=True,

    )
    state = FSMContext(storage, user=user_id, chat=user_id)
    await state.update_data(first_message=mes.message_id,
                            poll_question=0,
                            poll=tuple(map(lambda x: tuple(x), poll)),
                            poll_id=poll_id)
    await async_db.insert_or_update_main(
        user_id=user_id, main_id=mes.message_id, state="BotState:POLL"
    )
    await state.set_state(state_bot)


async def send_all_weekly_polls():
    user_list = await async_db.select_all_users(flag_init=False)
    for user in user_list:
        try:
            await call_weekly_polls(user[0])
        except Exception as e:
            logger.add(
                "file_1.log",
            )
            logger.info(f"{e} for telegram user {user[0]}. Please, try again.")
            logger.remove()
            continue
