from telebot import*
import random
import requests
from telebot.types import InputMediaPhoto
from dotenv import load_dotenv
import sqlite3
import json
from pathlib import Path
import os
import random
words = [' я', ' читал',' сегодня',' войну',' видел',' ты',' дорогой',' в',' завтра',' деп',' давай',' золото']
demid_word = ['топ', 'хороши челик','легенда','лучший','гений', 'наш слоняра!','пик человечества']

load_dotenv()
TOKEN ="7656035471:AAGXGG01QgXh7s4s6JkQf6vEB2kpoyBrmsI"
API_KEY ="AIzaSyDFKWIfpyRQM2VcW5a3ArQiv9mloH3-zJA"
SEARCH_ENGINE_ID ="155aabc4ca19e47cd"

bot = TeleBot(TOKEN)
name = ''
path = Path('blacklist.json')
path_searh = Path('searh.json')
blacklist = json.loads(path.read_text())

@bot.message_handler(commands=['start'])
def menu(message):
    markup = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton('текст', callback_data='text')
    btm2 = types.InlineKeyboardButton('картинка', callback_data='jpg')
    btm3 = types.InlineKeyboardButton('\tизменить\t', callback_data='edit')
    btm4 = types.InlineKeyboardButton('\tудалить\t', callback_data='delete')
    btm5 = types.InlineKeyboardButton('Восхвалить демида', callback_data='demid')
    markup.add(btm3)
    markup.add(btm4)
    markup.row(btm1, btm2)
    markup.add(btm5)
    bot.reply_to(message, 'Добрый день!')
    bot.send_message(message.chat.id, 'Чем займёмся?', reply_markup=markup)


@bot.message_handler(commands=['setnameuser'])
def set_name_user(message):
    sql = sqlite3.connect(f'database/{message.chat.title}.sql')
    cur = sql.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50))")
    sql.commit()
    cur.close()
    sql.close()

    bot.send_message(message.chat.id, 'Введи ник')
    bot.register_next_step_handler(message, set_name)

def set_name(message):
    global name
    name = message.text.strip()
    sql = sqlite3.connect(f'database/{message.chat.title}.sql')
    cur = sql.cursor()
    cur.execute(f"INSERT INTO users (name) VALUES ('%s')" % (name))
    sql.commit()
    cur.close()
    sql.close()
    bot.send_message(message.chat.id, f'Добавлен')


@bot.message_handler(commands=['all'])
def note_all(message):
    try:
        sql = sqlite3.connect(f'database/{message.chat.title}.sql')
        cur = sql.cursor()
        cur.execute(f"SELECT * FROM users")
        users = cur.fetchall()
        note = ''
        for user in users:
            note += f"{user[1]}\n"
        cur.close()
        sql.close()
        bot.send_message(message.chat.id, note)
    except sqlite3.OperationalError:
        pass

@bot.message_handler(commands=['add_blacklist'])
def add_blacklist(message):
    if message.from_user.id == 1488279593:
        bot.reply_to(message, 'Введите ник пользователя:')
        bot.register_next_step_handler(message, adding)
    else:
        bot.reply_to(message, 'У вас недостаточно прав')

def adding(message):
    global blacklist
    if message.from_user.id == 1488279593:
       blacklist.append(message.text)
       blacklist = json.dumps(blacklist)
       path.write_text(blacklist)
       blacklist = json.loads(path.read_text())

@bot.message_handler(commands=['check_search'])
def check_search(message):
    if message.from_user.id == 1488279593:
        result = ''
        content = json.loads(path_searh.read_text())
        for nickname, image in content.items():
            result += f'{nickname}: {image}\n'
        bot.send_message(message.chat.id, result) 


@bot.message_handler()
def send_info(message):
    text = message.text
    test = message.text.split()
    name = test[0]
    try:
        i = int(test[-1])
    except ValueError:
        pass
    else:
        if message.from_user.username not in blacklist:
            for _ in range(1, 10+1):
                bot.send_message(message.chat.id, test[0:-1])
    if name.strip().lower() == 'лохан':
        bot.send_message(message.chat.id, text[6:])
    elif text == 'скинь инфу':
        bot.send_message(message.chat.id, message)
    else:
        pass


@bot.callback_query_handler(func=lambda callback:True)
def callback_message(callback):
    if callback.data == 'text':
        i = random.randint(1, 12)
        mess = ''
        for _ in range(i):
            mess += random.choice(words)
        bot.send_message(callback.message.chat.id, mess)
    elif callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id-random.randint(1, 10))
    elif callback.data == 'edit':
        bot.edit_message_text('Изменённый текст!', callback.message.chat.id, callback.message.message_id-1)
    elif callback.data == 'jpg':
        if callback.message.from_user.username not in blacklist:
            bot.reply_to(callback.message, "Что ты хочешь увидеть? (Пиши на английском!)")
            bot.register_next_step_handler(callback.message, send_images)
        else:
            bot.send_message('Вам запрещено это делать')
    elif callback.data == 'demid':
        bot.send_message(callback.message.chat.id, f'Демид {random.choice(demid_word)}')

def send_images(message):
        try:
            if message.from_user.id != 1488279593:
                content = json.loads(path_searh.read_text())
                content[f'{message.from_user.username}{random.randint(1, 1000000)}'] = message.text
                content = json.dumps(content)
                path_searh.write_text(content)
            query = message.text
            if message.from_user.username not in blacklist:
                url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}&searchType=image"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                rndm_num = random.randint(1, 10)
                images = [item['link'] for item in data.get('items', [])[rndm_num:rndm_num+1]]
                
                if not images:
                    bot.reply_to(message, "По вашему запросу ничего не найдено 😢")
                    return

                media_group = [InputMediaPhoto(img) for img in images]
                bot.send_media_group(message.chat.id, media_group)
            else:
                bot.send_message('Вам запрещено это делать')
            
        except requests.exceptions.RequestException as e:
            bot.reply_to(message, f"Ошибка")
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка, лучше пиши на английском языке")

bot.polling(none_stop=True)