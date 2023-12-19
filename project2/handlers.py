# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor
import pymysql
import requests
from config import *

# Инициализация бота
bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message):
    # Проверка, является ли чат приватным
    if message.chat.type != "private":
        return
    else:
        # Подключение к БД
        connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        try:
            # Работа с БД
            with connection.cursor() as cursor:
                # Получение данных пользователя
                cursor.execute("SELECT * FROM users WHERE user_tgid=%s" % (message.from_user.id))
                res = cursor.fetchone()
                # Проверка полученных данных
                if res:
                    if len(res["user_apikey"]) > 0: 
                        await message.answer("✅Notifications are already set up!\nSend /stop to disable the bot.\nTo change the token, send a new one. To change the account, send a /auth login password.", )
                    else:
                        await message.answer("No notifications are configured. Send your token or /auth login password.", )
                else:
                    await message.answer("No notifications are configured. Send your token or /auth login password.", )
        finally:
            # Закрытие подключения к БД
            connection.close()

# Обработка команды /stop
@dp.message_handler(commands=['stop'])
async def cmd_stop(message):
    # Проверка, является ли чат приватным
    if message.chat.type != "private":
        return
    else:
        # Подключение к БД
        connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        try:
            # Работа с БД
            with connection.cursor() as cursor:
                # Получение данных пользователя
                cursor.execute("SELECT * FROM users WHERE user_tgid=%s" % (message.from_user.id))
                res = cursor.fetchone()
                # Проверка полученных данных и удаление токена
                if res:
                    if len(res["user_apikey"]) > 0: 
                        cursor.execute("UPDATE users SET user_apikey='' WHERE user_tgid=%s" % (message.from_user.id))
                        connection.commit()
                        await message.answer("✅Notifications have been successfully disabled.")
                    else:
                        await message.answer("🚫No notifications are configured. Send your token or /auth login password.")
                else:
                    await message.answer("🚫No notifications are configured. Send your token or /auth login password.")
        finally:
            # Закрытие подключения к БД
            connection.close()

# Авторизация при помощи логина и пароля (опционально TOTP)
@dp.message_handler(commands=['auth'])
@dp.message_handler(lambda message: len(message.text.split(' ')) == 2 or len(message.text.split(' ')) == 3)
async def plainauth(message):
    # Проверка, является ли чат приватным
    if message.chat.type != "private":
        return
    else:
        if message.is_command():
            msg_me = message.get_args().split(' ')  # Список аргументов команды (логин и пароль, опицонально TOTP)
        else:
            msg_me = message.text.split(' ') # Список аргументов команды (логин и пароль, опицонально TOTP)
        if len(msg_me) != 2 and len(msg_me) != 3:
            await message.answer("🚫It doesn't look like a username and password. Try again /auth login password.")
        else:
            # Подключение к БД
            connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
            try:
                # Работа с БД
                with connection.cursor() as cursor:
                    # Авторизация через API
                    if len(msg_me) == 2:
                        response = requests.post('https://HIDDEN_FOR_PRIVACY_REASONS/public/v1/login/', data={'username': msg_me[0], 'password': msg_me[1]})
                    elif len(msg_me) == 3:
                        requests.post('https://HIDDEN_FOR_PRIVACY_REASONS/public/v1/login/', data={'username': msg_me[0], 'password': msg_me[1]})
                        response = requests.post('https://HIDDEN_FOR_PRIVACY_REASONS/public/v1/two-factor-login/', data={'username': msg_me[0], 'password': msg_me[1], 'otp_token': msg_me[2]})
                    json = response.json()
                    # Обработка 2FA и ошибки 400
                    if 'requires_two_factor' in json:
                        await message.answer("To authorize, repeat the command, adding your 2FA code at the end (for example: /auth username pa$$word 123456)")
                    elif 'non_field_errors' in json:
                        if 'Please enter a correct username and password.' in json['non_field_errors']:
                            await message.answer("🚫Authorization error! Incorrect login or password!")
                        else:
                            await message.answer("🚫Authorization error! An unknown error has occurred!")
                    elif 'otp_token' in json:
                        if 'Invalid token or credentials has been expired.' in json['otp_token']:
                            await message.answer("🚫Authorization error! Incorrect login, password or 2FA code!")
                    elif response.status_code == 400:
                        await message.answer("🚫Authorization error for an unknown reason.")
                    elif 'token' not in json:
                        await message.answer("🚫Authorization error! API did not pass the token for an unknown reason without errors.")
                    else:
                        # Получение данных пользователя
                        cursor.execute("SELECT * FROM users WHERE user_tgid=%s" % (message.from_user.id))
                        res = cursor.fetchone()
                        # Запись полученных данных
                        if res:
                            cursor.execute("UPDATE users SET user_apikey='%s', user_lastorder=curtime() WHERE user_tgid=%s" % (json['token'], message.from_user.id))
                            await message.answer("✅API token registered successfully! You will now receive order notifications.")
                        else:
                            cursor.execute("INSERT INTO users SET user_tgid=%s, user_apikey='%s'" % (message.from_user.id, json['token']))
                            await message.answer("✅API token registered successfully! You will now receive order notifications.")
                        connection.commit()
                    await message.delete()
            except Exception as e:
                        await message.answer(e)
            finally:
                # Закрытие подключения к БД
                connection.close()

# Авторизация при помощи токена
@dp.message_handler(lambda message: len(message.text) > 128 and len(message.text) < 256)
async def token(message):
    # Проверка, является ли чат приватным
    if message.chat.type != "private":
        return
    else:
        # Подключение к БД
        connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        try:
            # Работа с БД
            with connection.cursor() as cursor:
                # Получение данных пользователя
                cursor.execute("SELECT * FROM users WHERE user_tgid=%s" % (message.from_user.id))
                res = cursor.fetchone()
                # Проверка полученных данных и запись токена
                if res:
                    cursor.execute("UPDATE users SET user_apikey='%s', user_lastorder=curtime() WHERE user_tgid=%s" % (message.text, message.from_user.id))
                    await message.answer("✅API token registered successfully! You will now receive order notifications.")
                else:
                    cursor.execute("INSERT INTO users SET user_tgid=%s, user_apikey='%s'" % (message.from_user.id, message.text))
                    await message.answer("✅API token registered successfully! You will now receive order notifications.")
                connection.commit()
        finally:
            # Закрытие подключения к БД
            connection.close()

if __name__ == '__main__':
    executor.start_polling(dp)

# v1.0.3
# 2021-03-15
