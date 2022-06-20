from time import sleep

import requests
import urllib3
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import (
    MessageToDeleteNotFound,
    MessageToEditNotFound,
    MessageNotModified,
    BotBlocked,
    TelegramAPIError,
    MessageCantBeDeleted,
    CantParseEntities, MessageIdentifierNotSpecified, MessageCantBeEdited, BadRequest,
)
from django.db.models import QuerySet
from loguru import logger



try:
    import async_db
    import liters
    import markup
    from create_bot import dp, storage
    from create_bot import loop
    from settings import BASE_DIR
except ModuleNotFoundError:
    from bot_marta import async_db
    from bot_marta import liters
    from bot_marta import markup
    from bot_marta.create_bot import dp, storage
    from bot_marta.create_bot import loop
    from bot_marta.settings import BASE_DIR
from aiogram.dispatcher.filters.state import State, StatesGroup


class BotState(StatesGroup):
    """Класс состояний бота."""

    ADMIN = State()
    STATE_0 = State()
    JOIN_NAME = State()
    ACCEPT_NAME = State()
    FACTS = State()
    MEETING = State()
    HOW_LONG_WORK = State()
    POLL1 = State()
    POLL2 = State()
    POLL3 = State()
    POLL_START = State()
    POLL_EVERYWEEK = State()
    GAME = State()
    MAIN = State()
    HELP = State()
    NEWSLETTER = State()
    NOTIFICATION = State()


async def delete_main_message(user_id: int, main_id: int):
    """Удаление главного сообщения."""
    try:
        await dp.bot.delete_message(chat_id=user_id, message_id=main_id)
    except (MessageToDeleteNotFound, MessageCantBeDeleted, MessageIdentifierNotSpecified, MessageNotModified, TelegramAPIError, BadRequest) as e:
        logger.add(
            "file_1.log",
        )
        logger.info(f"{e} for telegram user {user_id}. Please, try again.")
        logger.remove()
        try:
            await dp.bot.edit_message_text(text="⁠.", chat_id=user_id, message_id=main_id)
            await dp.bot.unpin_chat_message(chat_id=user_id, message_id=main_id)
        except (MessageToEditNotFound, MessageIdentifierNotSpecified, MessageNotModified, MessageCantBeEdited, TelegramAPIError, BadRequest):
            pass
        except Exception as e:
            logger.info(f"{e} for telegram user {user_id}. Please, try again.")
            logger.remove()


def answer_support(obj,):
    """Добавление ответа на вопрос пользователя из админки"""
    answer_dict = {False: 'дополнил(а) ответ', True: 'ответил(а)'}
    user_id, main_message, _, state = loop.run_until_complete(async_db.select_state(obj.question.member_id))[0]
    if state in ("BotState:MAIN", "BotState:HELP", "BotState:GAME", "BotState:NOTIFICATION", "BotState:NEWSLETTER"):
        loop.run_until_complete(
            delete_main_message(user_id=user_id, main_id=main_message)
        )

        mes = loop.run_until_complete(
            valid_parse_mode(
                dp.bot.send_message,
                user_id,
                liters.SUPPORT_ANSWER.format(
                    user=obj.user.first_name,
                    question=obj.question.text,
                    answer=obj.text,
                    type_answer=answer_dict[obj.is_answer()]
                ),
                reply_markup=markup.INLINE_KB_BACKMENU,
                parse_mode=types.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        )
        state = FSMContext(storage, user=user_id, chat=user_id)
        loop.run_until_complete(state.update_data(first_message=mes.message_id))
        loop.run_until_complete(state.set_state(BotState.MAIN))
        loop.run_until_complete(async_db.insert_or_update_main(
            user_id=user_id, main_id=mes.message_id, state="BotState:MAIN"
        ))


async def create_pin_message(user_id: int, main_id: int) -> types.Message:
    """Создание закрепленного сообщения"""
    try:
        request_pin = await async_db.get_pin_message()
        text_pin = request_pin[0][0]
    except KeyError:
        text_pin = liters.WELCOME3
    await delete_main_message(user_id, main_id)
    mes = await dp.bot.send_message(
        chat_id=user_id,
        text=text_pin,
        parse_mode=types.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
    await dp.bot.pin_chat_message(
        user_id,
        mes.message_id)
    await dp.bot.delete_message(
        user_id,
        mes.message_id+1
    )
    return mes.message_id


async def call_main(user_id: int):
    """Вызов главного меню"""
    request_state = await async_db.select_state(user_id=user_id)
    _, main_id, _, state = request_state[0]
    if state not in ("BotState:FACTS",
                     "BotState:MEETING",
                     "BotState:ACCEPT_NAME",
                     "BotState:JOIN_NAME",
                     ):

        await delete_main_message(user_id=user_id, main_id=main_id)
        mes = await dp.bot.send_message(
            chat_id=user_id,
            text=liters.MAIN_MENU + " ",
            reply_markup=markup.INLINE_KB_MAIN,
        )
        state = FSMContext(storage, user=user_id, chat=user_id)
        await state.update_data(first_message=mes.message_id)
        await async_db.insert_or_update_main(user_id=user_id, main_id=mes.message_id, state="BotState:MAIN")
        main_id = mes.message_id

    return main_id


def edit_pin_message(user_list: QuerySet, text: str):
    """Исправление закрепленного сообщения."""
    for user in user_list:
        if user.pin_message_id:
            try:
                # Исправить закрепленное сообщение
                loop.run_until_complete(
                    dp.bot.edit_message_text(
                        chat_id=int(user.member_id),
                        message_id=int(user.pin_message_id),
                        text=text,
                        parse_mode=types.ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )
                )
            except MessageNotModified:
                pass
            except (MessageToEditNotFound,):

                # Если было удалено, то удалить главное сообщение, прислать новое сообщение, прислать главное меню
                loop.run_until_complete(
                    delete_main_message(
                        user_id=user.member_id, main_id=user.main_message_id
                    )
                )

                main_id = loop.run_until_complete(call_main(user_id=user.member_id))
                pin = loop.run_until_complete(
                    dp.bot.send_message(
                        chat_id=int(user.member_id),
                        text=text,
                        parse_mode=types.ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )
                )
                state = FSMContext(storage, user=user.member_id, chat=user.member_id)
                loop.run_until_complete(
                    state.update_data(first_message=main_id)
                )
                loop.run_until_complete(async_db.insert_or_update_state(
                    user_id=user.member_id, main_id=main_id, pin_id=pin.message_id, state="BotState:MAIN"
                ))


def send_newsletter(user_list, text: str, photo: int):
    """Отправить рассылку всем пользователям.
    :param user_list - список пользователей;
    :param text - текст рассылки;
    :param photo - изображение.
    """
    for user in user_list:
        user_id, main_message, _, state_db = loop.run_until_complete(async_db.select_state(user_id=user.member_id))[0]

        if state_db in ("BotState:MAIN", "BotState:HELP", "BotState:GAME"):
            sleep(0.2)
            try:
                # Удалить главное сообщение
                try:
                    loop.run_until_complete(
                        delete_main_message(user_id=user_id, main_id=main_message)
                    )
                except (MessageToDeleteNotFound, MessageCantBeDeleted):
                    pass
                # Прислать сообщение рассылки
                if photo:
                    try:
                        mes = loop.run_until_complete(
                            valid_parse_mode(
                                dp.bot.send_photo,
                                user_id,
                                photo=open(
                                    BASE_DIR / "django_admin/static/{}".format(photo),
                                    "rb",
                                ),
                                caption=text,
                                reply_markup=markup.INLINE_KB_BACKMENU,
                                parse_mode=types.ParseMode.MARKDOWN,
                                disable_notification=True,
                            )
                        )

                    except TelegramAPIError:
                        mes = loop.run_until_complete(
                            valid_parse_mode(
                                dp.bot.send_message,
                                user_id,
                                text=text,
                                reply_markup=markup.INLINE_KB_BACKGAME,
                                parse_mode=types.ParseMode.MARKDOWN,
                                disable_web_page_preview=True,
                                disable_notification=True,
                            )
                        )
                else:
                    mes = loop.run_until_complete(
                        valid_parse_mode(
                            dp.bot.send_message,
                            chat_id=user_id,
                            text=text,
                            reply_markup=markup.INLINE_KB_BACKMENU,
                            parse_mode=types.ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                            disable_notification=True,
                        )
                    )
                state = FSMContext(storage, user=user_id, chat=user_id)
                loop.run_until_complete(state.update_data(first_message=mes.message_id))
                loop.run_until_complete(state.set_state(BotState.NEWSLETTER))
                loop.run_until_complete(async_db.insert_or_update_main(
                    user_id=user_id, main_id=mes.message_id, state="BotState:MAIN"
                ))
            except BotBlocked:
                # Отправка операторам уведомления, что пользователь заблокировал бота
                operators = loop.run_until_complete(async_db.select_operators())
                bot_user = loop.run_until_complete(async_db.select_user(tg_user_id=user_id))
                for operator in operators:
                    if operator[0]:
                        sleep(0.2)
                        try:
                            loop.run_until_complete(
                                dp.bot.send_message(
                                    chat_id=operator[0],
                                    text="Пользователь @{} заблокировал бота и не получит уведомление".format(
                                        bot_user[1]
                                    ),
                                )
                            )
                        except TelegramAPIError:
                            continue


async def valid_parse_mode(func, *args, **kwargs):
    """Валидация по методу парсинга сообщения"""
    try:
        result = await func(*args, **kwargs)
    except CantParseEntities:
        kwargs["parse_mode"] = None
        result = await func(*args, **kwargs)
    return result


async def request_portal(id):
    urllib3.disable_warnings()
    connect = requests.get(
        f'https://portal.mrtexpert.ru/api/users/{id}',
        headers={'Authorization': 'Token 98acb2d8373dde235d2773b42bcc5587'},
        verify=False
    )
    request = connect.json()
    name = (
        f"{request.get('lastname', None)} "
        f"{request.get('firstname', None)} "
        f"{request.get('middlename', None)}")
    unit = request.get('unit', None)
    region = request.get('region', None)
    try:
        unit = unit['name']
    except KeyError:
        unit = None
    return connect.status_code, name, unit, region


CONNECT_POLL = {
    btn: poll
    for btn, poll in list(zip([kb[1] for kb in markup.HOW_LONG_KB]
                              , (None, 1, 2, 3)))
}

POLL_STATE = {
    btn: poll
    for btn, poll in list(
        zip(
            [kb[1] for kb in markup.HOW_LONG_KB],
            (BotState.MAIN, BotState.POLL1, BotState.POLL2, BotState.POLL3),
        )
    )
}
