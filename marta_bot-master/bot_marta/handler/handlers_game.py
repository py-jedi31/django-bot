import asyncio
import random

from aiogram.utils.exceptions import TelegramAPIError
from loguru import logger

import async_db
import markup
import liters
from aiogram import types
from aiogram.dispatcher import FSMContext

from create_bot import dp, storage
from settings import BASE_DIR
from utils import BotState, delete_main_message


@dp.callback_query_handler(
    lambda c: c.data == "main_game",
    state=(BotState.MAIN, BotState.GAME),
)
async def start_game(callback_query: types.CallbackQuery, state: FSMContext):
    """Запускает случайный вопрос из общего списка, исключая уже заданные
    _____
    Кнопки:
    Срабатывание - "Поиграем?", "Ещё?"
    Создает - Кнопки вариантов ответа на вопрос.
    """
    await callback_query.answer()
    request_question = await random_question(callback_query.from_user.id)
    try:
        new_mes, options, haspicture = request_question
        await state.update_data(
            first_message=new_mes.message_id, haspicture=haspicture, options=tuple(map(lambda x: tuple(x), options))
        )
        await BotState.GAME.set()
    except (ValueError, TypeError):
        new_mes = await callback_query.message.edit_text(
            liters.NO_NEW_QUESTION,
            reply_markup=markup.INLINE_KB_BACKMENU,
        )
        await state.update_data(
            first_message=new_mes.message_id,
        )
    await async_db.insert_or_update_main(
        user_id=callback_query.from_user.id,
        main_id=new_mes.message_id,
        state=await state.get_state(),
    )


async def random_question(user_id: int):
    """
    Достает рандомный вопрос из БД , исключая уже заданные этому пользователю,
    и отправляет.

    :param user_id - id пользователя, которому отправится вопрос
      _____
    Кнопки:
    Срабатывание - "Поиграем?", "Ещё?"
    Создает - Кнопки вариантов ответа на вопрос.
    """

    request_question = await async_db.select_game_question(user_id=user_id)

    if request_question:
        question, options = request_question
        keyboard = markup.range_inline_kb(
            len(options), postfix="g", options=[o for _, o, _ in options], row_size=1
        )
        question_id, question_text, photo, cash = question
        user = await async_db.select_state(
            user_id=user_id
        )
        user_id, main_message, _, state_user = user[0]
        await delete_main_message(user_id, main_message)
        if not photo:
            new_mes = await dp.bot.send_message(
                user_id,
                question_text,
                reply_markup=keyboard,
            )
            haspicture = False
        else:
            new_mes = await send_photoquestion(
                user_id,
                question_id,
                question_text,
                photo,
                cash,
                keyboard,
            )
            haspicture = True
        return new_mes, options, haspicture
    return None


async def send_photoquestion(
    user_id: int, question_id: int, question_text: str, photo: str, cash: str, keyboard
) -> types.Message:
    """Отправка сообщения с фотографией. Если данное фото уже отправлялось в телеграм боте,
    то вызвать из кэша телеграмма"""
    if cash is not None:
        new_mes = await dp.bot.send_photo(
            user_id,
            photo=cash,
            caption=question_text,
            reply_markup=keyboard,
        )
    else:
        try:
            new_mes = await dp.bot.send_photo(
                user_id,
                photo=open(BASE_DIR / "django_admin/static/{}".format(photo), "rb"),
                caption=question_text,
                reply_markup=keyboard,
            )
            await async_db.insert_cash_photoquestion(
                question_id=question_id, cash=new_mes.photo[0]["file_id"]
            )
        except TelegramAPIError:
            new_mes = await dp.bot.send_message(
                user_id,
                text="Упс вопрос сломался",
                reply_markup=markup.INLINE_KB_BACKGAME,
            )
            # await async_db.delete_bag_question(question_id=question_id)
    return new_mes


async def send_question_all_users():
    """Массовая рассылка в определённое время."""
    user_list = await async_db.select_all_users()
    for user in user_list:
        await asyncio.sleep(0.2)
        try:
            request_question = await random_question(user[0])
            state = FSMContext(storage, user=user[0], chat=user[0])
            if request_question is not None:
                new_mes, options, haspicture = request_question
                await state.set_state(BotState.GAME)
                await state.update_data(
                    first_message=new_mes.message_id,
                    haspicture=haspicture,
                    options=tuple(map(lambda x: tuple(x), options)),
                )
                await async_db.insert_or_update_main(
                    user_id=user[0], main_id=new_mes.message_id, state="BotState:GAME"
                )
        except TelegramAPIError:
            logger.info(f"{user} заблокировал бота")
            continue


@dp.callback_query_handler(
    lambda c: c.data in map(lambda x: str(x) + "g", range(1, 6)),
    state=(BotState.MAIN, BotState.GAME, BotState.HELP),
)
async def answer_question_game(callback_query: types.CallbackQuery, state: FSMContext):
    """Выдает результат при ответе на вопрос. В случае верного ответа поздравит,
    неверного - скажет какой был правильный
    _____
    Кнопки:
    Срабатывание - Кнопки вариантов ответа на вопрос
    Создает -  "Ещё?", "В главное меню".
    """
    user_data = await state.get_data()
    answer = user_data["options"][int(callback_query.data.replace("g", "")) - 1]
    true_answer = [o for o in user_data["options"] if o[2]]
    if true_answer:
        true_answer = true_answer[0][1]
    await async_db.insert_game_answer(user_id=user_data["user_id"], option_id=answer[0])
    await delete_main_message(callback_query.from_user.id, callback_query.message.message_id)
    if answer[2]:
        new_mes = await callback_query.bot.send_message(
            callback_query.message.chat.id,
            random.choice(liters.TRUE_ANSWER).capitalize(),
            reply_markup=markup.INLINE_KB_BACKGAME,
        )
    else:
        new_mes = await callback_query.bot.send_message(
            callback_query.message.chat.id,
            random.choice(liters.FALSE_ANSWER).capitalize() + "\n" + true_answer,
            reply_markup=markup.INLINE_KB_BACKGAME,
        )
    await async_db.insert_or_update_main(
        user_id=callback_query.from_user.id,
        main_id=new_mes.message_id,
        state=await state.get_state(),
    )
    await state.update_data(first_message=new_mes.message_id, haspicture=False)
    await BotState.MAIN.set()
