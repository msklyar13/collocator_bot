import dict_functions
import dict_fill

# імпортуємо бібліотеку telebot для взаємодії з Телеграм ботом та під'єднуємось до конкретного бота за токеном
import telebot
from telebot import types
bot = telebot.TeleBot(
    'TOKEN', parse_mode='html')


# задаємо команду "/start" із першим повідомленням-привітанням бота та двома кнопками-опціями наступних дій для користувача
@bot.message_handler(commands=['start'])
def start(message):
    m = f'''Привіт, {message.from_user.first_name}!

Я бот, що увібрав у себе цілу колекцію словосполучень. Наразі доступні лише іменниково-прикметникові пари, але далі буде ;)
Ти можеш скористатись моїми знаннями для підбору придатного епітета, а можеш і сам(а) навчити мене новим словосполученням, додавши новий текст до мого корпусу.
                     
Що будемо робити?'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Підібрати епітет 🧩')
    btn2 = types.KeyboardButton('Додати текст 📝')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, m, reply_markup=markup)


# визначаємо повідомлення реакції на дві кнопки з першого блоку та відповідні блоки-функції, які оброблюватимуть подальший запит
@bot.message_handler(content_types=['text'])
def get_text(message):
    if message.text == 'Підібрати епітет 🧩':
        bot.send_message(
            message.chat.id, 'Прийшли мені іменник, до якого шукаєш епітети.')
        bot.register_next_step_handler(message, process_epithet)
    elif message.text == 'Додати текст 📝':
        bot.send_message(
            message.chat.id, 'Прийшли мені свій текст. Я опрацюю його та додам словосполучення до корпусу.')
        bot.register_next_step_handler(message, process_text_addition)
    else:
        bot.send_message(
            message.chat.id, 'Натисни одну з кнопок в меню, щоб продовжити взаємодію.')


# блок обробки повідомлення користувача на гілці "Підібрати епітет"
def process_epithet(message):
    respond_process_epithet(message)

# відповідь бота на запит користувача на гілці "Підібрати епітет" з використанням функції user_adjs_by_noun
def respond_process_epithet(message):
    bot.send_message(message.chat.id, user_adjs_by_noun(message.text.lower()))

# визначаємо функцію вилучення прикметників із БД за запитом-іменником через функцію exact_noun_adjs у файлі dict_fill
def user_adjs_by_noun(noun):
    if noun in dict_fill.exact_noun_adjs(noun):
        return '\n'.join(dict_fill.exact_noun_adjs(noun)[noun])
    else:
        return 'Іменника немає в словнику словосполучень.'


# блок обробки повідомлення користувача на гілці "Додати текст"
def process_text_addition(message):
    respond_process_text_addition(message)

# відповідь бота на запит користувача на гілці "Додати текст" з використанням функції user_text_to_dict
def respond_process_text_addition(message):
    bot.send_message(message.chat.id, user_text_to_dict(message.text))

# визначаємо функцію запису нового тексту до БД через функцію db_fill_update у файлі dict_fill
def user_text_to_dict(text):
    dict_fill.db_fill_update(dict_fill.nlp_text_to_dict(text))
    result = "\n".join([f"{key} — {', '.join(value)}" for key,
                       value in dict_fill.nlp_text_to_dict(text).items()])
    return f'''Базу даних оновлено. Знайдені словосполучення:\n{result}'''


# налаштовуємо постійний полінг з нульовим інтервалом на час активації програми
bot.polling(none_stop=True, interval=0)
