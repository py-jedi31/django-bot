from aiogram.utils.exceptions import TelegramAPIError

import async_db
import markup
import liters
from aiogram import types
from aiogram.dispatcher import FSMContext

from create_bot import dp
from utils import BotState, call_main, delete_main_message, create_pin_message


@dp.callback_query_handler(
    lambda c: c.data in [kb_data[1] for kb_data in markup.MAIN_KB[2:]],
    state=BotState.MAIN,
)
async def main_(callback_query: types.CallbackQuery):
    """Возвращает в главное меню с удалением всех предыдущих сообщений кроме закрепленного
     _____
    Кнопки:
    Срабатывание - 'Обучение','Опрос' (временно)
    Создает - 'Вернуться в главное меню'."""
    await callback_query.bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(
        "В разработке",
        reply_markup=markup.INLINE_KB_BACKMENU,
    )


@dp.callback_query_handler(
    lambda c: c.data == "back_main_btn",
    state=(
        BotState.MAIN,
        BotState.HELP,
        BotState.GAME,
        BotState.NEWSLETTER,
        BotState.NOTIFICATION,
    ),
)
async def main_menu_back(callback_query: types.CallbackQuery, state: FSMContext):
    """Возвращает в главное меню с удалением всех предыдущих сообщений кроме закрепленного
     _____
    Кнопки:
    Срабатывание - 'Вернуться в главное меню'
    Создает - главное меню('Поиграем?','Помощь','Обучение','Опрос')."""
    await BotState.MAIN.set()
    await callback_query.answer()

    user_data = await state.get_data()
    pin_mes_id = await create_pin_message(callback_query.from_user.id, user_data['pin_message'])
    await delete_main_message(user_id=callback_query.from_user.id, main_id=callback_query.message.message_id)
    new_mes = await callback_query.bot.send_message(
        callback_query.from_user.id,
        liters.MAIN_MENU,
        reply_markup=markup.INLINE_KB_MAIN,
    )
    await state.update_data(first_message=new_mes.message_id, pin_message=pin_mes_id)
    await async_db.insert_or_update_state(
        user_id=callback_query.from_user.id,
        main_id=new_mes.message_id,
        pin_id=pin_mes_id,
        state="BotState:MAIN"
    )


@dp.message_handler(state=BotState.MAIN)
async def waste_message(message: types.Message, state: FSMContext):
    """Выдает пользователю реакцию на написанное им сообщение, на которое не отвечают другие обработчики
    _____
    Кнопки:
    Создает - 'Задать этот вопрос оператору', 'Вернуться в главное меню'."""
    user_data = await state.get_data()
    if len(message.text) > 1900:
        await message.bot.edit_message_text(
            liters.HELP_QUESTION_OVERSIZE,
            message.from_user.id,
            user_data["first_message"],
        )
        await message.delete()
        return
    try:
        await message.bot.edit_message_text(
            liters.WASTE_MESSAGE.format(message.text),
            chat_id=message.chat.id,
            message_id=user_data["first_message"],
            reply_markup=markup.INLINE_KB_ASK_Q,
        )
    except TelegramAPIError:
        await delete_main_message(
            user_id=message.chat.id, main_id=user_data["first_message"]
        )
        mes = await message.bot.send_message(
            text=liters.WASTE_MESSAGE.format(message.text),
            chat_id=message.chat.id,
            reply_markup=markup.INLINE_KB_ASK_Q,
        )
        await state.update_data(first_message=mes.message_id)
    await state.update_data(user_question=message.text)
    await message.delete()
