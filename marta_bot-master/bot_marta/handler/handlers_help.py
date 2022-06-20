from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

import markup
import db
import liters

from utils import BotState
from create_bot import dp


@dp.callback_query_handler(lambda c: c.data == "help_web", state=BotState.MAIN)
async def help_web(callback_query: types.CallbackQuery):
    """Возвращает информацию по порталу
    _____
    Кнопки:
    Срабатывание - 'Вопросы по порталу'.
    Создает - 'Ссылка для входа', 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_WEB,
        reply_markup=markup.INLINE_KB_HELP_WEB,
    )


@dp.callback_query_handler(
    lambda c: c.data in ("main_help", "back_help_btn"),
    state=(BotState.MAIN, BotState.HELP),
)
async def support_menu(callback_query: types.CallbackQuery):
    """Возвращает в главное меню с удалением всех предыдущих сообщений кроме закрепленного
     _____
    Кнопки:
    Срабатывание - 'Помощь', 'Вернуться в меню помощи'
    Создает - главное меню('Вопросы по з/п',
                            'Вопросы по порталу',
                            'Вопросы по документам',
                            'Контакты департамента по работе с персоналом',
                            'Помощники с чат-ботом Марты',
                            'Задать свой вопрос',
                            'Вернуться в главное меню')."""
    await BotState.MAIN.set()
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_MENU,
        reply_markup=markup.INLINE_KB_HELP_MENU,
    )


@dp.callback_query_handler(lambda c: c.data == "help_doc", state=BotState.MAIN)
async def help_doc(callback_query: types.CallbackQuery):
    """Возвращает информацию по документам
    _____
    Кнопки:
    Срабатывание - 'Вопросы по документам'.
    Создает - 'Ссылка для входа', 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_DOC,
        reply_markup=markup.INLINE_KB_HELP_DOC,
    )


@dp.callback_query_handler(lambda c: c.data == "help_pay", state=BotState.MAIN)
async def help_pay(callback_query: types.CallbackQuery):
    """Возвращает информацию по документам
    _____
    Кнопки:
    Срабатывание - 'Вопросы по з/п'.
    Создает - 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_PAY,
        reply_markup=markup.INLINE_KB_BACKHELP,
    )


@dp.callback_query_handler(lambda c: c.data == "help_hr_contact", state=BotState.MAIN)
async def help_hr_сontacts(callback_query: types.CallbackQuery):
    """Возвращает информацию по контактам HR
    _____
    Кнопки:
    Срабатывание - 'контакты департамента по работе с персоналом'.
    Создает - 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_HR_CONTACT,
        reply_markup=markup.INLINE_KB_BACKHELP,
    )


@dp.callback_query_handler(lambda c: c.data == "help_bot_contact", state=BotState.MAIN)
async def help_bot_сontacts(callback_query: types.CallbackQuery):
    """Возвращает информацию по контактам HR
    _____
    Кнопки:
    Срабатывание - 'Помощники чат-бота Марты'.
    Создает - 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_BOT_CONTACT,
        reply_markup=markup.INLINE_KB_BACKHELP,
    )


@dp.callback_query_handler(lambda c: c.data == "help_ask", state=BotState.MAIN)
async def help_call(callback_query: types.CallbackQuery):
    """Предлагает пользователю задать свой вопрос
    _____
    Кнопки:
    Срабатывание - 'Задать свой вопрос'
    Создает - 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.HELP_CALL,
        reply_markup=markup.INLINE_KB_BACKHELP,
    )
    await BotState.HELP.set()


@dp.callback_query_handler(lambda c: c.data == "help_question", state=BotState.MAIN)
async def help_my_question(callback_query: types.CallbackQuery, state: FSMContext):
    """Возвращает информацию по заданному вопросу
    _____
    Кнопки:
    Срабатывание - 'Ваши вопросы'
    Создает - 'Вернуться в меню помощи'.
    """
    await callback_query.answer()
    user_data = await state.get_data()
    questions = db.select_user_question(user_id=user_data["user_id"])
    text_question = ""
    for question in db.select_user_question(user_id=user_data["user_id"]):
        if len(question) + len(text_question) < 3800:
            text_question += question + "\n"
    if questions:
        await callback_query.message.edit_text(
            liters.HELP_MY_QUESTION + text_question,
            reply_markup=markup.INLINE_KB_BACKHELP,
            disable_web_page_preview=True,
        )
    else:
        await callback_query.message.edit_text(
            liters.HELP_NOT_QUESTIONS,
            reply_markup=markup.INLINE_KB_BACKHELP,
            disable_web_page_preview=True,
        )


@dp.message_handler(state=BotState.HELP)
@dp.callback_query_handler(lambda c: c.data == "ask", state=BotState.MAIN)
async def help_ask_question(
    message: Union[types.Message, types.CallbackQuery], state: FSMContext
):
    """Возвращает сообщение об том, что вопрос задан
    _____
    Кнопки:
    Создает - 'Вернуться в главное меню'."""
    user_data = await state.get_data()
    operators = db.select_operators()

    if isinstance(message, types.Message):
        if len(message.text) > 1900:
            await dp.bot.edit_message_text(
                liters.HELP_QUESTION_OVERSIZE,
                message.from_user.id,
                user_data["first_message"],
            )
            await message.delete()
            return
        await dp.bot.edit_message_text(
            liters.HELP_GIVEN_QUESTION.format(message.text),
            message.from_user.id,
            user_data["first_message"],
            reply_markup=markup.INLINE_KB_BACKMENU,
        )
        db.insert_help_question(user_id=user_data["user_id"], text=message.text)
        await message.delete()
    else:
        await message.answer()
        await message.message.edit_text(
            liters.HELP_GIVEN_QUESTION.format(user_data["user_question"]),
            reply_markup=markup.INLINE_KB_BACKMENU,
        )
        db.insert_help_question(
            user_id=user_data["user_id"], text=user_data["user_question"]
        )
    for operator in operators:
        if operator[0]:
            if operator[0] != user_data["user_id"]:
                await dp.bot.send_message(
                    chat_id=operator[0],
                    text="У Вас новый вопрос от пользователя. Перейдите в панель администратора для ответа",
                )
    await BotState.MAIN.set()
