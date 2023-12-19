# -*- coding: utf-8 -*-
import logging
import hashlib
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle

import requests
from string import ascii_letters
symbols = ascii_letters + '_0123456789'

logging.basicConfig(level=logging.INFO)

bot = Bot(token="")
dp = Dispatcher(bot)
api_token = "https://HIDDEN_FOR_PRIVACY_REASONS/botapi.php?token=HIDDEN_FOR_PRIVACY_REASONS&"
support = "HIDDEN_FOR_PRIVACY_REASONS"

@dp.message_handler(commands=['start'])
async def cmd_start(message):
    msg_me = message.get_args()
    if len(msg_me) == 0:
        response = requests.get(api_token + "do=account&tgid=%s" % (message.from_user.id))
    else:
        response = requests.get(api_token + "do=account&tgid=%s&ref=%s" % (message.from_user.id, msg_me))
    if response.text == "true":
        await message.answer("Приветствую снова!\nДля быстрого входа в биллинг отправьте команду /login\nДля сброса или установки пароля — /password\nПоддержка: %s" % (support))
    elif response.text == "registred":
        await message.answer("Регистрация прошла успешно! Для заказа сервера свяжитесь с поддержкой %s.\nДля входа в биллинг отправьте команду /login\nДля сброса пароля — /password\nПоддержка: %s" % (support, support))
    elif response.text == "noref":
        await message.answer("Для регистрации нужно получить ссылку в поддержке.\nПоддержка: %s" % (support))
    elif response.text == "deny":
        await message.answer("Отказано в обслуживании.\nПоддержка: %s" % (support))
    elif response.text == "closed":
        await message.answer("Счёт закрыт.\nДля заказа сервера и активации аккаунта свяжитесь с поддержкой %s.\nДля входа в биллинг отправьте команду /login\nДля сброса пароля — /password\nПоддержка: %s" % (support, support))
    elif response.text == "deactivated":
        await message.answer("Учётная запись временно деактивирована.\nПоддержка: %s" % (support))
    elif response.text == "false":
        await message.answer("Ошибка API :(\nПоддержка: %s" % (support))
    else:
        await message.answer("Что-то пошло не так, попробуйте позже.\nВозможно сейчас проводятся технические работы.\nПоддержка: %s" % (support))

@dp.message_handler(commands=['login'])
async def cmd_start(message):
    response = requests.get(api_token + "do=wktoken2&tgid=%s&username=@%s" % (message.from_user.id, message.from_user.username))
    if response.status_code != 200 or response.text == "error":
        await message.answer("Что-то пошло не так, попробуйте позже.\nВозможно сейчас проводятся технические работы.\nПоддержка: %s" % (support))
    else:
        if response.text == "cooldown":
            await message.answer("Нельзя создавать более 10 токенов в час.")
        else:
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Войти", url="https://HIDDEN_FOR_PRIVACY_REASONS/quick.php?token=%s" % (response.text))
            keyboard.add(url_button)
            await message.answer("Осталось нажать на кнопку ниже :)", reply_markup=keyboard, disable_web_page_preview=True)

@dp.message_handler(commands=['reset', 'password'])
async def cmd_reset(message):
    response = requests.get(api_token + "do=resetpassword&tgid=%s" % (message.from_user.id))
    if response.status_code == 200 and len(response.text) > 0:
        if response.text == "false":
            await message.answer("Ошибка API :(\nПоддержка: %s" % (support))
        elif response.text == "deactivated":
            await message.answer("Учётная запись временно деактивирована.\nПоддержка: %s" % (support))
        elif response.text == "closed":
            await message.answer("Счёт закрыт.\nПоддержка: %s" % (support))
        elif response.text == "deny":
            await message.answer("Ошибка сброса пароля: отказано в обслуживании.\nПоддержка: %s" % (support))
        else:
            await message.answer("Пароль установлен!\n*Адрес биллинга:* https://HIDDEN_FOR_PRIVACY_REASONS\n*Telegram ID:* `%s`\n*Пароль:* `%s`\n\nДля смены логина или пароля нужно открыть меню _Аккаунт_ в биллинге.\nПоддержка: %s" % (message.from_user.id, response.text, support), parse_mode="Markdown")
    else:
        await message.answer("Что-то пошло не так, попробуйте позже.\nВозможно сейчас проводятся технические работы.\nПоддержка: %s" % (support))
executor.start_polling(dp)
