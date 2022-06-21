import requests
import urllib3
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted, MessageNotModified

import async_db
import markup
import liters
from settings import BASE_DIR
from utils import BotState, delete_main_message, call_main, request_portal, create_pin_message
from create_bot import dp


@dp.message_handler(commands=["start"])
async def start_messages(message: types.Message, state: FSMContext):
    """Приветствие пользователя
    ______
    Кнопки:
    -Привет, Марта.
    """
    args = message.get_args()
    user = await async_db.select_operator(args)

    if user or message.from_user.id in [1730515838, 932076209]:

        await message.answer(
            liters.WELCOME_ADMIN.format(*user), parse_mode=types.ParseMode.MARKDOWN
        )
        await async_db.update_operator(tg_id=message.from_user.id, username=user[0])
        await BotState.ADMIN.set()
        return
    elif args == "Pzs6_Gxa":
        new_mes = await message.answer(
            liters.WELCOME1,
            reply_markup=markup.INLINE_KB_WELCOME,
        )
        await message.delete()
        await state.update_data(first_message=new_mes.message_id)
        await BotState.STATE_0.set()
        return
    elif args:
        status_code, name, unit, region = await request_portal(args)

        if status_code == 200:
            await async_db.insert_user(
                user_id=message.from_user.id,
                user_name=name,
                user_name_tg=message.from_user.username,
                region=region,
                unit=unit,
            )

            await message.delete()
            mes = await message.answer(
                liters.NAME_ACCEPT.format(name),
                reply_markup=markup.INLINE_KB_FACT,
            )
            await state.update_data(
                user_name=name,
                user_name_tg=message.from_user.username,
                tg_user_id=message.from_user.id,
                user_id=message.from_user.id,
                answer_question_game=[],
                first_message=mes.message_id
            )
            await async_db.insert_or_update_main(
                user_id=message.from_user.id, main_id=mes.message_id
            )
            await BotState.ACCEPT_NAME.set()
        else:
            await message.answer_photo(
                photo=open(BASE_DIR / "django_admin/static/wrong_start.png", "rb"),
                caption=liters.WRONG_START
            )
    else:
        await message.answer_photo(
            photo=open(BASE_DIR / "django_admin/static/wrong_start.png", "rb"),
            caption=liters.WRONG_START
        )


@dp.callback_query_handler(
 lambda c: c.data == "welcome_btn", state=BotState.STATE_0
    )
async def welcome(callback_query: types.CallbackQuery):
    """Реакция на команду с клавиши Привет, Марта
    _____
    Кнопки:
    Срабатывание - "Привет, Марта"
    _____
    Переход в состояние Join_name."""
    await callback_query.answer()
    await callback_query.message.edit_text(liters.NAME_QUESTION)
    await BotState.JOIN_NAME.set()


@dp.callback_query_handler(
        lambda c: c.data == "ofcourse_btn",
        state=BotState.ACCEPT_NAME,
    )
async def fact(callback_query: types.CallbackQuery):
    """Реакция на команду с клавиши Конечно
    _____
    Кнопки:
    Срабатывание - "Конечно"
    Создает - "А ценности?"
    _____
    Переход в состояние FACTS."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.FIRST_FACT, reply_markup=markup.INLINE_KB_WORTH
    )
    await BotState.FACTS.set()


@dp.callback_query_handler(
        lambda c: c.data == "worth_btn",
        state=BotState.FACTS,
    )
async def worth(callback_query: types.CallbackQuery):
    """Реакция на команду с клавиши А ценности?
    _____
    Кнопки:
    Срабатывание - "А ценности?"
    Создает - "Да", "Нет".
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        liters.SECOND_FACT + "\n\n" + liters.W_METING_QUESTIONS,
        reply_markup=markup.INLINE_KB_METING,
    )
    await BotState.MEETING.set()


@dp.callback_query_handler(
        lambda c: c.data in [kb_data[1] for kb_data in markup.METING_KB],
        state=BotState.MEETING,
    )
async def welcome_meting(callback_query: types.CallbackQuery, state: FSMContext):
    """Узнает, об участии на Велком-встрече и выдает результат в соответствии с выбранным ответом
    _____
    Кнопки:
    Срабатывание - "Да", "Нет"
    Создает - "Далее".
    """
    await callback_query.answer()
    await state.update_data()
    text, link = liters.ANSWER_W_METING[callback_query.data]
    if callback_query.data == "no_meting_button":
        photo = open(BASE_DIR / "django_admin/static/Welcome.jpg", "rb")
        await delete_main_message(callback_query.from_user.id, callback_query.message.message_id)
        new_mes = await callback_query.bot.send_photo(
            callback_query.message.chat.id,
            photo=photo,
            caption=text,
            reply_markup=markup.kb_onwards_link(link),
        )
        await async_db.insert_or_update_main(
            user_id=callback_query.from_user.id, main_id=new_mes.message_id, state=await state.get_state()
        )
        await state.update_data(w_meeing=False, first_message=new_mes.message_id, pin_message=None)
    else:
        await callback_query.message.edit_text(
            text,
            reply_markup=markup.kb_onwards_link(link),
        )
        await state.update_data(w_meeing=True, pin_message=None)


@dp.callback_query_handler(
        lambda c: c.data in ("onward_btn", "main_poll"),
        state=(BotState.MEETING, BotState.MAIN),
    )
async def how_long_work(callback_query: types.CallbackQuery, state: FSMContext):
    """Выдает вопрос по длительности работы в компании
    _____
    Кнопки:
    Срабатывание - "Далее"
    Создает - "Менее двух недель", "2 - 6 недель", '6 - 12 недель', "Более 12 недель".
    _____
    Переходит в состояние HOW_LONG_WORK.
    """
    await callback_query.answer()
    user_data = await state.get_data()
    await BotState.HOW_LONG_WORK.set()
    if not user_data["w_meeing"]:
        await delete_main_message(callback_query.from_user.id, callback_query.message.message_id)
        new_mes = await callback_query.bot.send_message(
            callback_query.message.chat.id,
            liters.HOW_LONG_WORK,
            reply_markup=markup.INLINE_KB_HOW_LONG,
        )
        await state.update_data(first_message=new_mes.message_id,
                                )
        await async_db.insert_or_update_main(user_id=callback_query.from_user.id,
                                             main_id=new_mes.message_id,
                                             state=await state.get_state())
    else:
        await callback_query.message.edit_text(
            liters.HOW_LONG_WORK,
            reply_markup=markup.INLINE_KB_HOW_LONG,
        )


@dp.message_handler(state=BotState.JOIN_NAME)
async def request_name(message: types.Message, state: FSMContext):
    """Запись имени пользователя.
    ____
    Кнопки:
    Создает - "Конечно".
    """
    name = message.text
    await async_db.insert_user(
        user_id=message.from_user.id,
        user_name=name.title(),
        user_name_tg=message.from_user.username,
    )

    await state.update_data(
        user_name=name.title(),
        user_name_tg=message.from_user.username,
        tg_user_id=message.from_user.id,
        user_id=message.from_user.id,
        answer_question_game=[],
    )
    await message.delete()
    user_data = await state.get_data()
    await message.bot.edit_message_text(
        liters.NAME_ACCEPT.format(name.title()),
        message.from_user.id,
        user_data["first_message"],
        reply_markup=markup.INLINE_KB_FACT,
    )
    await async_db.insert_or_update_main(
        user_id=message.from_user.id, main_id=user_data["first_message"], state="BotState:ACCEPT_NAME"
    )
    await BotState.ACCEPT_NAME.set()


@dp.message_handler(commands=["re"], state='*' )
async def restart(message: types.Message, state: FSMContext):
    """Перезагружает скрипт (функция для разработки)."""
    user_data = await state.get_data()
    await message.delete()
    await state.reset_state()
    try:
        await delete_main_message(
            message.chat.id, user_data["first_message"]
        )
        await delete_main_message(
            message.chat.id, user_data["pin_message"]
        )
    except (MessageToDeleteNotFound, MessageCantBeDeleted):
        pass
    except KeyError:
        return
    await message.answer(
        liters.RESTART_BOT, parse_mode=types.ParseMode.MARKDOWN
    )
    await async_db.del_user(message.from_user.id)


@dp.message_handler(
    commands=["main", "start"],
    state=(
        BotState.MAIN,
        BotState.HELP,
        BotState.GAME,
        BotState.NEWSLETTER,
        BotState.NOTIFICATION,
        BotState.POLL1,
        BotState.POLL2,
        BotState.POLL3,
        BotState.POLL_START,
        BotState.POLL_EVERYWEEK,
        BotState.HOW_LONG_WORK,
    ),
)
async def call_main_menu(message: types.Message, state: FSMContext):
    """Выдает главное меню пользователю
    _____
    Кнопки:
    Создает - главное меню('Поиграем?','Помощь','Обучение','Опрос')."""
    await message.delete()
    user_data = await state.get_data()
    try:
        await delete_main_message(
            message.chat.id, user_data["pin_message"]
        )
    except (MessageToDeleteNotFound, MessageCantBeDeleted, MessageNotModified):
        pass
    except (KeyError, TypeError):
        pass
    pin_id = await create_pin_message(message.chat.id, user_data["first_message"])
    main_id = await call_main(message.chat.id)
    await async_db.insert_or_update_state(
        user_id=message.from_user.id,
        pin_id=pin_id,
        main_id=main_id,
        state="BotState:MAIN",
    )
    await BotState.MAIN.set()
    await state.update_data(first_message=main_id, pin_message=pin_id)


@dp.message_handler(
    commands=["main", "start"],
    state=BotState.ACCEPT_NAME,
)
async def facts_mes(message: types.Message, state: FSMContext):
    """Повтор сообщения "Реакция на команду с клавиши Конечно"
    на случай, если случайно удалили главное сообщение.
    _____
    Кнопки:
    Срабатывание - "Конечно"
    Создает - "А ценности?"
    """
    await message.delete()
    user_data = await state.get_data()
    await delete_main_message(message.from_user.id, user_data["first_message"])
    mes = await message.answer(
        liters.FIRST_FACT,
        reply_markup=markup.INLINE_KB_WORTH
    )
    await state.update_data(
        first_message=mes.message_id
    )
    await async_db.insert_or_update_main(
        user_id=message.from_user.id, main_id=mes.message_id, state="BotState:ACCEPT_NAME"
    )
    await BotState.FACTS.set()


@dp.message_handler(
    commands=["main", "start"],
    state=(BotState.FACTS,
           BotState.MEETING)
)
async def worth_mes(message: types.Message, state: FSMContext):
    """Повтор сообщения "Реакция на команду с клавиши А ценности?"
    на случай, если случайно удалили главное сообщение.
    _____
    Кнопки:
    Срабатывание - "А ценности?"
    Создает - "Да", "Нет".
    """
    await message.delete()
    user_data = await state.get_data()
    await delete_main_message(message.from_user.id, user_data["first_message"])
    mes = await message.answer(
        liters.SECOND_FACT + "\n\n" + liters.W_METING_QUESTIONS,
        reply_markup=markup.INLINE_KB_METING,
    )
    await state.update_data(
        first_message=mes.message_id
    )
    await async_db.insert_or_update_main(
        user_id=message.from_user.id, main_id=mes.message_id, state="BotState:MEETING"
    )
    await BotState.MEETING.set()


@dp.message_handler(
    state=(
        BotState.STATE_0,
        BotState.MEETING,
        BotState.FACTS,
        BotState.ACCEPT_NAME,
        BotState.HOW_LONG_WORK,
        BotState.GAME,
        BotState.NEWSLETTER,
        BotState.NOTIFICATION,
    ),
)
async def del_waste(message: types.Message):
    """Удаляет сообщения пользователя , когда он не должен писать"""
    await message.delete()
