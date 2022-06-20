WELCOME1 = "Привет! Меня зовут Марта, я твой помощник. Я буду с тобой на протяжении трёх месяцев, пока ты знакомишься с компанией и со своей должностью."
WELCOME2 = "Нажми кнопку «Привет, Марта»"
WELCOME3 = "В закреплённых сообщениях книги [«Скорость доверия»](https://mybook.ru/author/stiven-kovi/skorost-doveriya-to-chto-menyaet-vsyo/read/) и [«Искренний сервис»](https://mybook.ru/author/maksim-nedyakin/iskrennij-servis-kak-motivirovat-sotrudnikov-sdela/read/) - обязательно прочитай их. Они помогут тебе быстрее узнать культуру компании."
WELCOME_ADMIN = """Приветствую тебя администратор, здесь будут приходить уведомления о том, что кому-то потребовалась твоя помощь

Вот [ссылка](https://marta.talestorm.ru/admin/) на вход в панель администратора.
Логин: {0}
Пароль нужно получить у главного администратора.
"""

RESTART_BOT = """Бот остановлен, для старта зайди в [профиль на портале](https://portal.mrtexpert.ru/profile/edit) и нажми "Перейти" """
WRONG_START = """
Привет! Мне сложно понять как тебя зовут и откуда ты.
Для связи стоит нажимать на кнопку ПЕРЕЙТИ в своём профиле на портале в поле Telegram.
Не стоит писать мне /start и запускать как-то по-другому.
"""
NAME_QUESTION = "Как тебя зовут?"
NAME_ACCEPT = "Поздравляю {}, теперь ты часть успешной команды! Я хочу рассказать тебе интересные факты о компании. Начнём?"

FIRST_FACT = "Круто! Каждый твой коллега знает нашу цель и ценности. Это нужно для того, чтобы наш вектор развития был единым. Наша глобальная цель – везде, где мы есть, обеспечить каждому обратившемуся к нам человеку простой и понятный способ удовлетворения своих медицинских потребностей с высоким качеством и гарантией результата"
SECOND_FACT = """В нашей компании живут 5 ключевых ценностей - ДОЗОР.
ДОЗОР - это:
🤝Доверие - открытое, честное, уважительное поведение в интересах себя и других людей,
👍Ответственность - готовность отвечать за выбор действия или бездействия,
😇Забота - предложить помощь и решить ситуацию,
💪Оптимизм - ты можешь всё, во что веришь,
👨‍🎓Развитие - я сегодня лучше, чем вчера!

Я надеюсь, что тебе близки наши ценности и ты разделяешь их)"""

W_METING_QUESTIONS = "Скажи, ты принимал(а) участие в Welcome-встрече?"
ANSWER_W_METING = {
    "yes_meting_button": (
        "Молодец! Перейди по ссылке, нам важно твоё мнение о встрече!",
        'https://docs.google.com/forms/d/1MoDHP7e3n6AJ20PpW0RrRs2i8LL6r2yG4QuRE04UehQ',
    ),
    "no_meting_button": (
        "Тогда, вот твоё приглашение. Мы будем ждать тебя",
        'https://us02web.zoom.us/j/82390931572?pwd=WFA5VzRjaFNTL3ZFbVF2c2E3QmJCdz09'
    ),
}

HOW_LONG_WORK = "Выбери, сколько ты работаешь в компании?"

INSTRUCTION_POLL = "Для того, чтобы помочь нам улучшить процесс адаптации, тебе нужно пройти небольшой опрос.{}"
INTRODUCTION_FOR_WEEKLY_POLL = {4: " Он еженедельный, но в дальнейшем он будет сильно короче)",
                                5: ""}
NOT_TODAY = "Первый опрос по адаптации будет через 2 недели после начала работы"
CONGRATULATION = """Благодарим тебя за активность! Ты ответил(а) на вопросы и твоя обратная связь поможет нам выстроить 
процесс адаптации ещё лучше! Сейчас ты увидишь мое активное меню. Можешь выбирать любой раздел, который тебе интересен.
"""

MAIN_MENU = """Главное меню
🎲 Поиграем: в этом разделе у тебя будет возможность проверить свои знания и поиграть со мной
📚 Обучение: раздел, где хранятся важные и полезные материалы
🧑🏻‍💻 Помощь : возникли вопросы? - смело задавай их в этом разделе
🕵️‍♂️ Опрос: твоя обратная связь - ценный ресурс, делись своим мнением и мыслями в этом разделе"""

TRUE_ANSWER = (
    "Молодец!",
    "Да, ты прав(а)!",
    "Молодец! Не ожидала, что ты знаешь)",
    "Это правильный ответ)",
    "Верно!",
    "Точно)",
)

FALSE_ANSWER = (
    "Неправильно!",
    "Неверно(",
    "Согласна, сложный вопрос",
    "Нет.",
    "Ответ неверный",
)

ONWORDS_GAME = (
    "Дальше?",
    "Продолжаем?",
    "Ещё?",
    "Ещё вопрос?",
    "Играем дальше?",
)

NO_NEW_QUESTION = "Мы отлично поиграли. Приходи за новыми вопросами на следующей неделе"

HELP_MENU = "Выбери интересющую тебя категорию вопросов. Если нет необходимой категории, задай вопрос. Мы соединим тебя со специалистом"

HELP_WEB = """Портал - информационное сердце нашей компании, где у тебя есть возможность найти необходимый документ или сотрудника, пройти обучение и заглянуть в корпоративную библиотеку, оставить свою идею по улучшению компании, а также познакомиться с другими его разделами.
Если у тебя есть вопрос по порталу, ты можешь задать его Поповой Дарье (почта - dpopova@mrtexpert.ru, скайп - @popova_dasha3) """

HELP_DOC = """На портале в разделе документы ты можешь найти и скачать необходимую информацию.
Или можешь задать вопрос мне в разделе “Вопросы”.
"""

HELP_PAY = """Заработная плата выплачивается 2 раза в месяц перечислением на карту сотрудника - аванс 30, зарплата 15 числа.
Если возникнут вопросы по начисленной заработной плате, обратитесь к бухгалтеру.
"""

HELP_HR_CONTACT = """Константинова Елена Александрова (директор по персоналу)
eakonstantinova@mrtexpert.ru

Королева Светлана Юрьевна (руководитель бизнес-школы)
skoroleva@mrtexpert.ru

Налимова Марина Владимировна (руководитель отдела по по подбору персонала)
mvnalimova@mrtexpert.ru
"""

HELP_BOT_CONTACT = """Кунгурова Екатерина Владимировна (менеджер по обучению и адаптации)
ekungurova@mrtexpert.ru

Попова Дарья Викторовна (менеджер по обучению и адаптации)
dpopova@mrtexpert.ru
"""

HELP_CALL = """Напишите вопрос, мы его передадим оператору"""

HELP_MY_QUESTION = """Ваши вопросы: \n"""
HELP_NOT_QUESTIONS = """У вас нет заданных вопросов"""

HELP_GIVEN_QUESTION = """Ты задал(а) вопрос:

{}

В ближайшее время мои помощницы ответят тебе, а пока можете перейти обратно в главное меню"""
HELP_QUESTION_OVERSIZE = """Вопрос не должен превышать 1900 символов. Попробуйте повторить вопрос"""

WASTE_MESSAGE = """Обычно, я не отвечаю на такие сообщения. Возможно, ты хочешь задать свой вопрос оператору?
Я повторю Ваш вопрос:
{}

Если помощь оператора не нужна, нажмите "Вернуться в главное меню" """

SUPPORT_ANSWER = """Помощник {user} {type_answer} на твой вопрос:
{question}
Ответ: {answer}
"""
