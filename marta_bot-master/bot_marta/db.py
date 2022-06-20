import random

import psycopg2
from datetime import datetime

try:
    import settings
except ModuleNotFoundError:
    from bot_marta import settings

DATABASE = {
    "dbname": settings.DATABASES["default"]["NAME"],
    "user": settings.DATABASES["default"]["USER"],
    "password": settings.DATABASES["default"]["PASSWORD"],
    "host": settings.DATABASES["default"]["HOST"],
}


def psycopg2_cursor(conn_info):
    """Декоратор для оборачивания функций, работающих с БД."""

    def wrap(f):
        def wrapper(*args, **kwargs):
            try:
                # Открыть соединение с бд
                connection = psycopg2.connect(**conn_info)
                cursor = connection.cursor()

                # Вызов функции с курсором
                return_val = f(cursor, *args, **kwargs)
                connection.commit()
            finally:
                # Закрыть соединение
                connection.close()

            return return_val

        return wrapper

    return wrap


@psycopg2_cursor(DATABASE)
def insert_user(cursor, user_id: int, user_name: str, user_name_tg: str):
    """Добавление новых пользователей."""
    cursor.execute(
        """SELECT * FROM member WHERE tg_id=%s""",
        (user_id,),
    )
    result = cursor.fetchall()
    if result:
        del_user(user_id=user_id)
    cursor.execute(
        """INSERT INTO member(tg_id, tg_name, name) VALUES (%s,%s,%s)""",
        (
            user_id,
            user_name_tg,
            user_name,
        ),
    )


@psycopg2_cursor(DATABASE)
def del_user(cursor, user_id: str):
    """Удалить данные о пользователе"""
    cursor.execute(
        """DELETE FROM member WHERE tg_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM member_state WHERE member_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM poll_questionanswer WHERE member_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM poll_answer WHERE member_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM game_answer WHERE member_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM call_support_answeroperator USING call_support_memberquestion
         WHERE question_id = call_support_memberquestion.id AND call_support_memberquestion.member_id=%s""",
        (user_id,),
    )
    cursor.execute(
        """DELETE FROM call_support_memberquestion WHERE member_id=%s""",
        (user_id,),
    )


@psycopg2_cursor(DATABASE)
def insert_answer(cursor, user_id: int, question_id: int, answer: str):
    """Добавление новых ответов пользователя."""
    cursor.execute(
        """INSERT INTO poll_questionanswer(member_id, question_id, answer, date) VALUES (%s,%s,%s,%s)""",
        (user_id, question_id, answer, datetime.now()),
    )


@psycopg2_cursor(DATABASE)
def insert_poll_answer(cursor, user_id: int, poll_id: int):
    """Добавление новых ответов пользователя."""
    cursor.execute(
        """INSERT INTO poll_answer(member_id, poll_id, date) VALUES (%s,%s,%s)""",
        (user_id, poll_id, datetime.now()),
    )


@psycopg2_cursor(DATABASE)
def select_poll(cursor, poll_id: int):
    """Получение опроса."""
    cursor.execute(
        """SELECT poll_question.id, poll_question.text,
                  poll_questionoptions.count_key, 
                  poll_questionoptions.text_key, 
                  poll_question.text_answer
                    FROM poll_question
                    INNER JOIN poll_questionoptions ON poll_questionoptions.id = poll_question.options_id
                    WHERE poll_id = (%s)
                    ORDER BY poll_question.id""",
        (poll_id,),
    )
    return cursor.fetchall()


@psycopg2_cursor(DATABASE)
def select_game_question(cursor, user_id: int):
    """Получение вопросов интерактива."""
    cursor.execute(
        """SELECT id, text, picture, cash
                    FROM game_question   
                    WHERE id NOT IN (
                        SELECT game_questionoptions.question_id
                        FROM game_answer
                        JOIN game_questionoptions ON game_answer.option_id = game_questionoptions.id
                        WHERE member_id = (%s)
                        ) AND is_active = true                               
                    """,
        (user_id,),
    )
    result = cursor.fetchall()
    if not result:
        return None
    question = random.choice(result)
    cursor.execute(
        """SELECT id, text, true_answer
                        FROM game_questionoptions   
                        WHERE question_id = (%s)                                    
                        """,
        (question[0],),
    )
    options = cursor.fetchall()
    return question, options


@psycopg2_cursor(DATABASE)
def insert_game_answer(cursor, user_id: int, option_id: int):
    """Добавление новых ответов пользователя."""
    cursor.execute(
        """INSERT INTO game_answer(member_id, option_id, date) VALUES (%s,%s,%s)""",
        (user_id, option_id, datetime.now()),
    )


def insert_help_question(user_id: int, text: str):
    """Добавление новых ответов пользователя."""
    connect = psycopg2.connect(**DATABASE)
    curs = connect.cursor()
    curs.execute(
        """INSERT INTO call_support_memberquestion(member_id, text, date) VALUES (%s,%s,%s)""",
        (user_id, text, datetime.now()),
    )
    connect.commit()
    curs.execute(
        """SELECT id
                    FROM call_support_memberquestion
                    WHERE member_id = (%s) AND text = (%s)""",
        [user_id, text],
    )
    result = curs.fetchall()[-1]
    curs.execute(
        """INSERT INTO call_support_answeroperator(user_id, question_id, date_create, date_update)
         VALUES (%s,%s,%s,%s)""",
        (None, result, datetime.now(), datetime.now()),
    )
    connect.commit()
    curs.close()
    connect.close()


@psycopg2_cursor(DATABASE)
def select_user_question(
    cursor,
    user_id: int,
):
    """Получение вопросов пользователя ."""
    cursor.execute(
        """SELECT  call_support_memberquestion.text, call_support_answeroperator.text
                    FROM call_support_answeroperator   
                    JOIN call_support_memberquestion 
                    ON call_support_answeroperator.question_id = call_support_memberquestion.id
                    WHERE member_id = (%s)
                    ORDER BY call_support_memberquestion.date DESC
                    """,
        (user_id,),
    )
    result = cursor.fetchall()
    questions = []
    for ques, ans in result:
        if ans is None:
            ans = "------"
        questions.append(f"\nВопрос: {ques}\nОтвет: {ans}\n")
    return questions


@psycopg2_cursor(DATABASE)
def select_user(cursor, tg_user_id: int):
    """Получение данных о пользователе."""
    cursor.execute(
        """SELECT *
                    FROM member
                    WHERE tg_id = (%s)""",
        (tg_user_id,),
    )
    return cursor.fetchall()[-1]


@psycopg2_cursor(DATABASE)
def insert_or_update_main(
    cursor,
    user_id: int,
    main_id: int,
    state: str=None
):
    """Добавление или обновление состояния пользователя."""
    cursor.execute(
        """INSERT INTO member_state (member_id, main_message_id, state) VALUES (%s, %s, %s)
        ON CONFLICT (member_id) DO UPDATE SET main_message_id = (%s), state = (%s)""",
        [user_id, main_id, state, main_id, state],
    )


@psycopg2_cursor(DATABASE)
def insert_or_update_state(
    cursor,
    user_id: int,
    main_id: int,
    pin_id: int,
    state: str=None
):
    """Добавление или обновление состояния пользователя."""
    cursor.execute(
        """INSERT INTO member_state (member_id, main_message_id, pin_message_id, state) VALUES (%s, %s, %s, %s)
        ON CONFLICT (member_id) DO UPDATE SET main_message_id = (%s), pin_message_id = (%s), state = (%s) """,
        [user_id, main_id, pin_id, state, main_id, pin_id, state],
    )


@psycopg2_cursor(DATABASE)
def get_pin_message(cursor):
    """Получить закрепленное сообщение."""
    cursor.execute(
        """SELECT text FROM call_support_pinmessage 
        """
    )
    return cursor.fetchall()


@psycopg2_cursor(DATABASE)
def select_state(cursor, user_id: int):
    """Получить состояние пользователя."""
    cursor.execute(
        """SELECT * FROM member_state WHERE member_id = (%s) 
        """,
        [
            user_id,
        ],
    )
    return cursor.fetchall()


@psycopg2_cursor(DATABASE)
def select_operators(cursor):
    """Получить tg_id операторов."""
    cursor.execute(
        """SELECT telegram_id FROM user_admin
        """,
    )
    return cursor.fetchall()


@psycopg2_cursor(DATABASE)
def update_operator(cursor, tg_id: int, username: str):
    """Обновить tg_id оператора."""
    cursor.execute(
        """UPDATE user_admin SET telegram_id = (%s) WHERE username = (%s) AND telegram_id IS NULL
        """, (tg_id, username,) #
    )
    del_user(user_id=tg_id)


@psycopg2_cursor(DATABASE)
def select_operator(cursor, username: str):
    """Обновить tg_id оператора."""
    cursor.execute(
        """SELECT username FROM user_admin WHERE username = (%s) 
        """, (username,)
    )
    return cursor.fetchone()


@psycopg2_cursor(DATABASE)
def insert_cash_photoquestion(cursor, question_id: int, cash: str):
    """Добавить кэш-Id фотографии ранее присланной в боте к вопросу."""
    cursor.execute(
        """UPDATE game_question SET cash = (%s) WHERE id = (%s)""", (cash, question_id)
    )


@psycopg2_cursor(DATABASE)
def insert_cash_photo(cursor, letter_id: int, cash: str):
    """Добавить кэш-Id фотографии ранее присланной в боте к рассылке."""
    cursor.execute(
        """UPDATE call_support_newsletter SET cash = (%s) WHERE id = (%s)""", (cash, letter_id)
    )


@psycopg2_cursor(DATABASE)
def delete_bag_question(cursor, question_id: int):
    """Удалить вопрос, который не может отправить телеграм."""
    cursor.execute(
        """DELETE FROM game_questionoptions WHERE question_id=%s""",
        (question_id,),
    )
    cursor.execute(
        """DELETE FROM game_question WHERE id=%s""",
        (question_id,),
    )


@psycopg2_cursor(DATABASE)
def select_all_users(cursor):
    """Выбрать всех пользователей, чье состояние после MainMenu."""
    cursor.execute(
        """SELECT member_id FROM member_state WHERE state 
        IN ('BotState:GAME', 'BotState:HELP', 'BotState:MAIN') """
    )
    result = cursor.fetchall()
    if result is None:
        return []
    return result

