import asyncio
import random

import asyncpg
from datetime import datetime
# Импортируем settings.py
try:
    import settings
except ModuleNotFoundError:
    from bot_marta import settings
# Создаем базу данных
DATABASE = {
    "database": settings.DATABASES["default"]["NAME"],
    "user": settings.DATABASES["default"]["USER"],
    "password": settings.DATABASES["default"]["PASSWORD"],
    "host": settings.DATABASES["default"]["HOST"],
}


def psycopg2_cursor(conn_info):
    """Декоратор для оборачивания функций, работающих с БД."""

    def wrap(f):
        async def wrapper(*args, **kwargs):
            try:
                # Открыть соединение с бд
                connection = await asyncpg.connect(**conn_info)

                # Вызов функции с курсором
                return_val = await f(connection, *args, **kwargs)

            finally:
                # Закрыть соединение
                await connection.close()

            return return_val

        return wrapper

    return wrap


"""Функции с пользователями"""
@psycopg2_cursor(DATABASE)
async def insert_user(
        conn,
        user_id: int,
        user_name: str,
        # date: datetime=None,
        user_name_tg: str,
        region: str = None,
        unit: str = None,

):
    """Добавление новых пользователей."""
    result = await conn.fetch(
        """SELECT * FROM member WHERE tg_id=$1""",
        user_id,
    )
    if result:
        await del_user(user_id=user_id)
    await conn.execute(
        """INSERT INTO member(tg_id, tg_name, name, region, unit, date) VALUES ($1,$2,$3,$4,$5,$6)""",
        user_id,
        user_name_tg,
        user_name,
        region,
        unit,
        datetime.today()
    )


@psycopg2_cursor(DATABASE)
async def del_user(conn, user_id: int):
    """Удалить данные о пользователе"""
    MEMBER_TABLE_SHIP = (
        'call_support_memberquestion',
        'member_state',
        'poll_questionanswer',
        'poll_answer',
        'game_answer',
                         )
    await conn.execute(
        """DELETE FROM call_support_answeroperator USING call_support_memberquestion
         WHERE question_id = call_support_memberquestion.id AND call_support_memberquestion.member_id=$1""",
        user_id,
    )
    for name_table in MEMBER_TABLE_SHIP:
        await conn.execute(
            """DELETE FROM {} WHERE member_id=$1""".format(name_table),
            user_id,
        )
    await conn.execute(
        """DELETE FROM member WHERE tg_id=$1""",
        user_id,
    )


@psycopg2_cursor(DATABASE)
async def select_user(cursor, tg_user_id: int):
    """Получение данных о пользователе."""
    return await cursor.fetchrow(
        """SELECT *
                    FROM member
                    WHERE tg_id = $1""",
        tg_user_id,
    )


@psycopg2_cursor(DATABASE)
async def insert_or_update_main(
    conn,
    user_id: int,
    main_id: int,
    state: str = None,
    has_init_poll: bool = False,
):
    """Добавление или обновление состояния пользователя."""
    await conn.execute(
        """INSERT INTO member_state (member_id, main_message_id, state, has_init_poll) VALUES ($1, $2, $3, $4)
        ON CONFLICT (member_id) DO UPDATE SET main_message_id = $2, state = $3""",
        user_id, main_id, state, has_init_poll,
    )


@psycopg2_cursor(DATABASE)
async def select_all_users(connection, flag_init=False):
    """Выбрать всех пользователей, чье состояние после MainMenu."""
    if not flag_init:
        sql_request = """SELECT member_id FROM member_state WHERE state
            NOT IN ('BotState:FACTS', 'BotState:MEETING', 'BotState:ACCEPT_NAME','BotState:JOIN_NAME') """
    else:
        sql_request = """SELECT member_state.member_id
         FROM member_state 
            JOIN member ON member_state.member_id = member.tg_id 
            WHERE member_state.state NOT IN ('BotState:FACTS', 'BotState:MEETING', 'BotState:ACCEPT_NAME','BotState:JOIN_NAME') 
            AND member.date + integer '14' < CURRENT_DATE 
                    """

    result = await connection.fetch(
        sql_request
    )
    if result is None:
        return []
    return result


@psycopg2_cursor(DATABASE)
async def insert_or_update_state(
    conn,
    user_id: int,
    main_id: int,
    pin_id: int,
    state: str = None,
    has_init_poll: bool = False,
):
    """Добавление или обновление состояния пользователя."""
    if not has_init_poll:
        sql_request = """INSERT INTO member_state (member_id, main_message_id, pin_message_id, state, has_init_poll) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (member_id) DO UPDATE SET main_message_id = $2, pin_message_id = $3, state = $4"""
    else:
        sql_request = """INSERT INTO member_state (member_id, main_message_id, pin_message_id, state, has_init_poll) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (member_id) DO UPDATE SET main_message_id = $2, pin_message_id = $3, state = $4, has_init_poll = $5"""
    await conn.execute(
        sql_request,
        user_id, main_id, pin_id, state, has_init_poll,
    )


@psycopg2_cursor(DATABASE)
async def select_state(conn, user_id: int, with_init_poll=False):
    """Получить состояние пользователя."""
    if not with_init_poll:
        sql_request = """SELECT member_id, main_message_id,
         pin_message_id, state FROM member_state WHERE member_id = $1"""
    else:
        sql_request = """SELECT * FROM member_state WHERE member_id = $1"""
    return await conn.fetch(
        sql_request,
        user_id,
    )


"""Функции с опросами"""
@psycopg2_cursor(DATABASE)
async def insert_answer(cursor, user_id: int, question_id: int, answer: str):
    """Добавление новых ответов пользователя."""
    await cursor.fetch(
        """INSERT INTO poll_questionanswer(member_id, question_id, answer, date) VALUES ($1,$2,$3,$4)
        ON CONFLICT (member_id, question_id, date) DO UPDATE SET answer=$3""",
        user_id, question_id, answer, datetime.now(),
    )


@psycopg2_cursor(DATABASE)
async def insert_poll_answer(conn, user_id: int, poll_id: int):
    """Добавление новых ответов пользователя."""
    await conn.execute(
        """INSERT INTO poll_answer(member_id, poll_id, date) VALUES ($1,$2,$3)
        ON CONFLICT (member_id, poll_id, date) DO UPDATE SET poll_id=$2""",
        user_id, poll_id, datetime.now(),
    )


@psycopg2_cursor(DATABASE)
async def select_poll(conn, poll_id: int):
    """Получение опроса."""
    return await conn.fetch(
        """SELECT poll_question.id, poll_question.text,
                  poll_questionoptions.count_key,
                  poll_questionoptions.text_key,
                  poll_question.text_answer
                    FROM poll_question
                    INNER JOIN poll_questionoptions ON poll_questionoptions.id = poll_question.options_id
                    WHERE poll_id = $1
                    ORDER BY poll_question.id""",
        poll_id,
    )


"""Функции с интерактивом"""
@psycopg2_cursor(DATABASE)
async def select_game_question(conn, user_id: int):
    """Получение вопросов интерактива."""
    result = await conn.fetch(
        """SELECT id, text, picture, cash
                    FROM game_question
                    WHERE id NOT IN (
                        SELECT game_questionoptions.question_id
                        FROM game_answer
                        JOIN game_questionoptions ON game_answer.option_id = game_questionoptions.id
                        WHERE member_id = $1
                        ) AND is_active = true
                    """,
        user_id,
    )
    if not result:
        return None
    question = random.choice(result)
    options = await conn.fetch(
        """SELECT id, text, true_answer
                        FROM game_questionoptions
                        WHERE question_id = $1
                        """,
        question[0],
    )
    return question, options


@psycopg2_cursor(DATABASE)
async def insert_game_answer(cursor, user_id: int, option_id: int):
    """Добавление новых ответов пользователя."""
    await cursor.execute(
        """INSERT INTO game_answer(member_id, option_id, date) VALUES ($1,$2,$3)""",
        user_id, option_id, datetime.now(),
    )


@psycopg2_cursor(DATABASE)
async def delete_bag_question(connection, question_id: int):
    """Удалить вопрос, который не может отправить телеграм."""
    await connection.execute(
        """DELETE FROM game_questionoptions WHERE question_id=$1""",
        question_id,
    )
    await connection.execute(
        """DELETE FROM game_question WHERE id=$1""",
        question_id,
    )


@psycopg2_cursor(DATABASE)
async def insert_cash_photoquestion(conn, question_id: int, cash: str):
    """Добавить кэш-Id фотографии ранее присланной в боте к вопросу."""
    await conn.execute(
        """UPDATE game_question SET cash = $1 WHERE id = $2""", cash, question_id
    )


"""Функции с разделом "Помощь"."""
@psycopg2_cursor(DATABASE)
async def select_user_question(
    conn,
    user_id: int,
):
    """Получение вопросов пользователя ."""
    result = await conn.fetch(
        """SELECT  call_support_memberquestion.text, call_support_answeroperator.text
                    FROM call_support_answeroperator
                    JOIN call_support_memberquestion
                    ON call_support_answeroperator.question_id = call_support_memberquestion.id
                    WHERE member_id = $1
                    ORDER BY call_support_memberquestion.date DESC
                    """,
        user_id,
    )
    questions = []
    for ques, ans in result:
        if ans is None:
            ans = "------"
        questions.append(f"\nВопрос: {ques}\nОтвет: {ans}\n")
    return questions


@psycopg2_cursor(DATABASE)
async def get_pin_message(conn):
    """Получить закрепленное сообщение."""
    return await conn.fetch(
        """SELECT text FROM call_support_pinmessage
        """
    )


@psycopg2_cursor(DATABASE)
async def insert_cash_photo(conn, letter_id: int, cash: str):
    """Добавить кэш-Id фотографии ранее присланной в боте к рассылке."""
    await conn.execute(
        """UPDATE call_support_newsletter SET cash = $1 WHERE id = $2""", cash, letter_id
    )


@psycopg2_cursor(DATABASE)
async def insert_help_question(conn, user_id: int, text: str):
    """Добавление новых ответов пользователя."""
    await conn.execute(
        """INSERT INTO call_support_memberquestion(member_id, text, date) VALUES (%s,%s,%s)""",
        (user_id, text, datetime.now()),
    )
    result = await conn.fetch(
        """SELECT id
                    FROM call_support_memberquestion
                    WHERE member_id = (%s) AND text = (%s)""",
        [user_id, text],
    )
    result = result[-1]
    await conn.execute(
        """INSERT INTO call_support_answeroperator(user_id, question_id, date_create, date_update)
         VALUES (%s,%s,%s,%s)""",
        (None, result, datetime.now(), datetime.now()),
    )


"""Функции с администраторами бота"""
@psycopg2_cursor(DATABASE)
async def select_operators(conn):
    """Получить tg_id операторов."""
    return await conn.fetch(
        """SELECT telegram_id FROM user_admin
        """,
    )


@psycopg2_cursor(DATABASE)
async def update_operator(conn, tg_id: int, username: str):
    """Обновить tg_id оператора."""
    await conn.execute(
        """UPDATE user_admin SET telegram_id = $1 WHERE username = $2 AND telegram_id IS NULL
        """, tg_id, username,
    )
    await del_user(user_id=tg_id)


@psycopg2_cursor(DATABASE)
async def select_operator(conn, username: str):
    """Проверка оператора."""
    return await conn.fetchrow(
        """SELECT username FROM user_admin WHERE username = $1
        """, username,
    )


# if __name__ == '__main__':
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     user_list = loop.run_until_complete(select_all_users(flag_init=False))
#     for user in user_list:
#         print(user)
