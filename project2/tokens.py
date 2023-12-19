# -*- coding: utf-8 -*-
import pymysql
import time
import requests
import schedule
from config import *

def newtoken():
        while True:
            try:
                # Подключение к БД
                connection = pymysql.connect(host=mysql_host,user=mysql_user,password=mysql_password,db=mysql_db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
                # Работа с БД
                try:
                    with connection.cursor() as cursor:
                        numrows = cursor.execute("SELECT * FROM users")
                        # Что-то происходит xD. Слава Україні! (интересно, это кто-то вообще прочитает?)
                        res = cursor.fetchall()
                        i = 0
                        while i < numrows:
                            response = requests.post('https://HIDDEN_FOR_PRIVACY_REASONS/public/v1/token/refresh/', data={'token': res[i]['user_apikey']})
                            json = response.json()
                            if len(json['token']) > 128:
                                cursor.execute("UPDATE users SET user_apikey='%s' WHERE user_id=%s" % (response.json()['token'], res[i]['user_id']))
                            i += 1
                            time.sleep(10)
                        connection.commit()
                except Exception:
                    pass
            finally:
                connection.close()

schedule.every(3).hours.do(newtoken)

while True:
    schedule.run_pending()
    time.sleep(1)

# v1.0.3
# 2021-03-15
