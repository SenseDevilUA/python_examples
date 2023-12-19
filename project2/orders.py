# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor
import pymysql
import time
import datetime
import requests
import asyncio
from config import *

# Инициализация бота (только для отправки сообщений)
bot = Bot(token=telegram_token)

async def main():
    while True:
        # Подключение к БД
        connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        try:
            # Работа с БД
            with connection.cursor() as cursor:
                numrows = cursor.execute("SELECT * FROM users")
                # Что-то происходит xD. Слава Україні! (интересно, это кто-то вообще прочитает?)
                res = cursor.fetchall()
                i = 0
                while i < numrows:
                    try:
                        if(len(res[i]['user_apikey']) >= 128):
                            ots = time.mktime(datetime.datetime.strptime(str(res[i]['user_lastorder']), "%Y-%m-%d %H:%M:%S").timetuple())
                            response = requests.get('https://HIDDEN_FOR_PRIVACY_REASONS/public/v1/user/orders/?closed_at__gte=%s' % (int(ots)),
                            headers={'Authorization': 'JWT ' + res[i]['user_apikey']}
                            )
                            list_ = response.json()
                            if response.status_code == 200:
                                lenlist = len(list_)
                                if lenlist > 0:
                                    ii = 0
                                    while ii < lenlist:
                                        if int(list_[ii]['closed_at']) > int(ots):
                                            # Пара должна отображаться ссылкой (к следующему апдейту)
                                            ovolume = '{:.8f}'.format(float(list_[ii]['volume'])).rstrip('0')
                                            osum = '{:.8f}'.format(float(list_[ii]['sum'])).rstrip('0')
                                            if list_[ii]['type'] == 'buying':
                                                await bot.send_message(res[i]['user_tgid'], "New closed order!\nType: %s🟢\nUnit price: %s\nVolume: %s\nSum: %s\nPair: %s" % (list_[ii]['type'], list_[ii]['unit_price'], ovolume, osum, list_[ii]['pair']))
                                            elif list_[ii]['type'] == 'selling':
                                                await bot.send_message(res[i]['user_tgid'], "New closed order!\nType: %s🔴\nUnit price: %s\nVolume: %s\nSum: %s\nPair: %s" % (list_[ii]['type'], list_[ii]['unit_price'], ovolume, osum, list_[ii]['pair']))
                                        ii += 1
                                        time.sleep(0.1)
                                    lo_ts = datetime.datetime.utcfromtimestamp(int(list_[0]['closed_at'])).strftime('%Y-%m-%d %H:%M:%S')
                                    cursor.execute("UPDATE users SET user_lastorder='%s' WHERE user_id=%s" % (lo_ts, res[i]['user_id']))
                            elif response.status_code == 401:
                                cursor.execute("UPDATE users SET user_apikey='' WHERE user_id=%s" % (res[i]['user_id']))
                                await bot.send_message(res[i]['user_tgid'], "Your API token is invalid and has been removed from the bot")
                                # await bot.send_message(res[i]['user_tgid'], "Your API token is invalid and has been removed from the bot")
                                #if response.text == '{"detail":"Error decoding signature."}':
                                #    cursor.execute("UPDATE users SET user_apikey='' WHERE user_id=%s" % (res[i]['user_id']))
                                #    await bot.send_message(res[i]['user_tgid'], "Your API token is invalid and has been removed from the bot")
                                #elif response.text == '{"detail":"Signature has expired."}':
                                #    cursor.execute("UPDATE users SET user_apikey='' WHERE user_id=%s" % (res[i]['user_id']))
                                #    await bot.send_message(res[i]['user_tgid'], "Your API token expired and has been removed from the bot")
                        i += 1
                    except Exception:
                        pass
                connection.commit()
        finally:
            connection.close()
        time.sleep(10)

while True:
    asyncio.run(main())
    time.sleep(1)
# v1.0.2
# 2021-03-15
