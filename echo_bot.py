import telebot
import datetime
from telebot import types
from connectdb import Interrogation, Subject, db, User
from config import TOKEN

# You can set parse_mode by default. HTML or MARKDOWN
bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    user_exists = db.query(User).filter_by(name=name).first()
    if not user_exists:
        new_user = User(name=message.from_user.first_name)
        db.add(new_user)
        db.commit()
        bot.reply_to(
            message, "Hello, welcome to scheduled bot, you're registred. To get more information tap /help")
    else:
        bot.reply_to(
            message, "You're already registerd , /help - to start " + name)


@bot.message_handler(commands=['info'])
def send_help(message):
    subjects = db.query(Subject).all()
    if not subjects:
        bot.send_message(message.chat.id, "no info, sorry")
    else:
        j = ""
        for subject in subjects:
            j += "Subject: " + subject.name + "\n"
            for inter in subject.interrogations:
                j += "Interrogation name: " + inter.name + "," + \
                    " Interrogation date: " + str(inter.date) + "\n"
        bot.send_message(message.chat.id, j)


@bot.message_handler(commands=['subjects'])
def show_subjects(message):
    subjects = db.query(Subject).all()
    if not subjects:
        bot.send_message(message.chat.id, "no subjects, sorry")
    else:
        j = ""
        for subject in subjects:
            j += "Subject: " + subject.name + "\n"

        bot.send_message(message.chat.id, j)


@bot.message_handler(commands=['help'])
def send_help(message):
    m = "Avaibale commands: \n /users - to get a list of users \n /info - list of all subjects and information about interrogations, exams, ds... \n /subjects - list of all subjects \n /add_subject <name> - to add a new subject \n /add_interro - to add new interrogation , /i <name> : <date> , date-fromat = `y-m-d` "
    bot.send_message(message.chat.id, m)


@bot.message_handler(commands=['users'])
def show_users(message):
    users = db.query(User).all()
    users_to_display = []

    for user in users:
        users_to_display.append(user.name)

    st = "Current users: \n"

    if len(users_to_display) == 0:
        st += "no users, sorry"
    else:
        for user in users_to_display:
            st += f"{user} \n"

    bot.send_message(message.chat.id, st)


@bot.message_handler(commands=['add_subject'])
def add_subject(message):
    name = message.text[13:]
    if len(name) == 0 or len(name) >= 8 or not name.isalpha():
        bot.send_message(message.chat.id, "incorrect subject provided, sorry")
    else:
        subject_exists = db.query(Subject).filter_by(name=name).first()

        if not subject_exists:
            new_subject = Subject(name=name)
            db.add(new_subject)
            db.commit()
            bot.reply_to(
                message, "new subject added!")
        else:
            bot.reply_to(
                message, f"Subject {name} already exists")


@bot.message_handler(commands=['add_interro'])
def add_interro(message):
    keyboard = []

    subjects = db.query(Subject).all()

    if not subjects:
        bot.send_message(message.chat.id, "no subjects, sorry")
    else:
        for subject in subjects:
            keyboard.append([types.InlineKeyboardButton(
                subject.name, callback_data=subject.id)])

        reply_markup = types.InlineKeyboardMarkup(keyboard)

        bot.send_message(message.chat.id, "choose your subject:",
                         reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda query: int(query.data) in range(0, 100))
def process_callback(query):
    # bot.edit_message_text(
    #     query.message.chat.id, query.message.message_id, "")

    subject_id = query.data

    bot.send_message(query.message.chat.id,
                     "enter interrogation name and date, '/i name : yyyy-mm-dd'")

    @bot.message_handler(content_types=["text"], commands=["i"])
    def process_name_step(message):
        if len(message.text) == 0:
            bot.send_message(
                message.chat.id, "text and time are not provided, sorry")
        else:
            name, date = message.text.split(":")
            new_name = name[2::]
            new_date = date.strip()
            format = "%Y-%m-%d"
            if len(new_name) >= 20 or not new_name.isalpha():
                bot.send_message(
                    message.chat.id, "incorrect name format, sorry")
            else:
                try:
                    datetime.datetime.strptime(new_date, format)
                    year, month, day = new_date.split('-')
                    datetime.datetime(year=int(year),month=int(month),day=int(day))
                    new_interro = Interrogation(
                        name=new_name, date=date, subject_id=subject_id)
                    db.add(new_interro)
                    db.commit()
                    bot.send_message(
                        message.chat.id, "new interrogation added!")
                except ValueError:
                    bot.send_message(
                        message.chat.id, "incorrect date format, sorry")


bot.infinity_polling()
