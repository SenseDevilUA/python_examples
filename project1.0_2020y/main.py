# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
import random
import hashlib
import pymysql
from pymysql.cursors import DictCursor

bot = Bot(token="", parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message):
   connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='bot',
    charset='utf8mb4',
    cursorclass=DictCursor
   )
   msg_me = message.get_args()
   try:
      with connection.cursor() as cursor:
         user_count=cursor.execute("SELECT user_id FROM users WHERE user_login='%s'" % (message.from_user.id))
      if user_count > 0:
         await message.answer("У вас есть аккаунт!\nВаш ID (логин): <pre>%s</pre>\n\nЕсли вы забыли пароль, свяжитесь с HIDDEN_FOR_PRIVACY_REASONS" % (message.from_user.id))
      else:
         if len(msg_me) == 0:
            if user_count == 0:
               await message.answer("Вы не зарегистрированы! Перейдите по ссылке от партнёра.")
               
         else:
            with connection.cursor() as cursor:
               ref_count=cursor.execute("SELECT user_id FROM users WHERE user_ref_link='%s'" % (msg_me))
               if(ref_count == 1):
                  for row in cursor:
                     ref_id = row['user_id']
                  passw = ''
                  for x in range(16):
                     passw = passw + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwz'))
                  passwo = hashlib.sha256(str(passw).encode('utf-8'))
                  password = passwo.hexdigest()
                  cursor.execute("INSERT INTO users SET user_login='%s', user_tgnickname='@%s', user_password='%s', user_ref='%d'" % (message.from_user.id, message.from_user.username, str(password), ref_id))
                  connection.commit()
                  await message.answer("Ваш аккаунт создан!\nАдрес панели (ACHTUNG! ЭТО БИЛЛИНГ, НЕ СЕРВЕР): https://HIDDEN_FOR_PRIVACY_REASONS/\n\nID (логин): <pre>%s</pre>\nПароль: <pre>%s</pre>" % (message.from_user.id, passw))
               else:
                  await message.answer("Ссылка от партнёра недействительна!")
   except Exception as e:
      await message.answer("Возникла ошибка. Свяжитесь с HIDDEN_FOR_PRIVACY_REASONS")
   connection.close()

@dp.message_handler(commands=['balance'])
async def cmd_balance(message):
   connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='bot',
    charset='utf8mb4',
    cursorclass=DictCursor
   )
   try:
      with connection.cursor() as cursor:
         user_count=cursor.execute("SELECT user_id FROM users WHERE user_login='%s'" % (message.from_user.id))
      if user_count < 1:
         await message.answer("Вы не зарегистрированы! Перейдите по ссылке от партнёра.")
      else:
         with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET user_tgnickname='@%s' WHERE user_login='%s'" % (message.from_user.username, message.from_user.id))
            user_info_data=cursor.execute("SELECT * FROM users WHERE user_login='%s'" % (message.from_user.id))
            if(user_info_data == 1):
               for row in cursor:
                  balance = row['user_balance']
                  refbalance = row['user_refbalance']
         if float(refbalance) > 0:
            await message.answer("Ваш баланс: %d €\nВаш партнёрский баланс: %d €\nВы можете пополнить основной баланс командой /invoice СУММА В EUR" % (balance, refbalance))
         else:
            await message.answer("Ваш баланс: %d €\nВы можете пополнить его командой /invoice СУММА В EUR" % (balance))
   except Exception as e:
      await message.answer("Возникла ошибка. Свяжитесь с HIDDEN_FOR_PRIVACY_REASONS")
   connection.commit()
   connection.close()
   
@dp.message_handler(commands=['2fa'])
async def cmd_2fa(message):
   connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='bot',
    charset='utf8mb4',
    cursorclass=DictCursor
   )
   try:
      with connection.cursor() as cursor:
         user_count=cursor.execute("SELECT user_id FROM users WHERE user_login='%s'" % (message.from_user.id))
      if user_count < 1:
         await message.answer("Вы не зарегистрированы! Перейдите по ссылке от партнёра.")
      else:
         with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET user_tgnickname='@%s' WHERE user_login='%s'" % (message.from_user.username, message.from_user.id))
            user_info_data=cursor.execute("SELECT * FROM users WHERE user_login='%s'" % (message.from_user.id))
            if(user_info_data == 1):
               for row in cursor:
                  status2fa = row['user_2fa_status']
         if status2fa == 'true':
            await message.answer("У вас уже включена двухфакторная авторизация. Вы можете отключить её в панели.")
         else:
            with connection.cursor() as cursor:
               cursor.execute("UPDATE users SET user_2fa_status='true' WHERE user_login='%s'" % (message.from_user.id))
               connection.commit()
            await message.answer("Двухфакторная авторизация включена! Теперь вы будете получать коды в Telegram.")
   except Exception as e:
      await message.answer("Возникла ошибка. Свяжитесь с HIDDEN_FOR_PRIVACY_REASONS")
   connection.commit()
   connection.close()

@dp.message_handler(commands=['invoice'])
async def cmd_invoice(message):
   connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='bot',
    charset='utf8mb4',
    cursorclass=DictCursor
   )
   msg_me = message.get_args()
   try:
      if len(msg_me) == 0:
         await message.answer("Укажите сумму от 5 € до 10000 € (например /invoice 100)")
      elif int(msg_me) < 5 or int(msg_me) > 10000:
         await message.answer("Неправильная сумма. Укажите целое число от 5 до 10000 €")
      else:
         if int(msg_me) > 5:
            with connection.cursor() as cursor:
               user_count=cursor.execute("SELECT user_id FROM users WHERE user_login='%s'" % (message.from_user.id))
            if user_count < 1:
               await message.answer("Вы не зарегистрированы! Перейдите по ссылке от партнёра.")
            else:
               with connection.cursor() as cursor:
                  cursor.execute("UPDATE users SET user_tgnickname='@%s' WHERE user_login='%s'" % (message.from_user.username, message.from_user.id))
                  user_info_data=cursor.execute("SELECT user_id FROM users WHERE user_login='%s'" % (message.from_user.id))
                  if(user_info_data == 1):
                     for row in cursor:
                        user_id = row['user_id']
            await message.answer("<a href='https://rf.cryptonator.com/api/merchant/v1/startpayment/?merchant_id=HIDDEN_FOR_PRIVACY_REASONS&item_name=HIDDEN_FOR_PRIVACY_REASONS&invoice_amount=%s&invoice_currency=eur&order_id=bot_%s'>Перейдите по ссылке для оплаты</a>" % (msg_me, user_id))
         
   except Exception as e:
      await message.answer("Возникла ошибка. Свяжитесь с HIDDEN_FOR_PRIVACY_REASONS")
   connection.commit()
   connection.close()

executor.start_polling(dp)
