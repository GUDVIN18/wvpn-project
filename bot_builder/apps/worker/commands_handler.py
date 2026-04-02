from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from apps.bot.models import Bot_Message, Bot_Button, BotUser, Text_Castom, Referal, PaymentReferal
from apps.worker.models import Events
import requests
from datetime import datetime
import pandas as pd
import time
from threading import Thread
from datetime import timedelta
import openai
from open_ai import interact_with_assistant
from apps.bot.service import create_payment
import asyncio
import re
from translate import translate
import random
import string
import locale
from collections import defaultdict
from django.db import models
from decimal import Decimal
import subprocess
from apps.bot.marzban_user_api import create_user_api, update_user_api
# Переводчик
# from deep_translator import GoogleTranslator

# def translate_message(text: str, target_lang: str = 'en') -> str:
#     try:
#         translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
#         return translated
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text

def build_bot_keyboards(buttons: list[Bot_Button], language_chooce):
    inline_rows = defaultdict(lambda: [None] * 4)  # 4 позиции в ряду
    reply_rows = defaultdict(lambda: [None] * 4)

    for button in buttons:
        button: Bot_Button
        btn_text = translate(button.text, language_chooce)

        try:
            pos = int(button.button_position or 99)
        except ValueError:
            pos = 99

        row = (pos - 1) // 4         # 1–4 → 0, 5–8 → 1, ...
        col = (pos - 1) % 4          # 1 → 0, 2 → 1, ..., 4 → 3

        # Inline кнопки
        if button.type_btn == "Inline":
            if button.type_data == 'data':
                inline_rows[row][col] = InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"{button.data} {button.text}"
                )
            elif button.type_data == 'url':
                inline_rows[row][col] = InlineKeyboardButton(
                    text=btn_text,
                    url=button.data
                )

            elif button.type_data == 'web_app':
                inline_rows[row][col] = InlineKeyboardButton(
                    text=btn_text,
                    web_app=WebAppInfo(url=button.data)
                )

        # Reply кнопки
        elif button.type_btn == "Reply":
            if button.type_data == 'data':
                reply_rows[row][col] = KeyboardButton(text=btn_text)
            elif button.type_data == 'url':
                reply_rows[row][col] = KeyboardButton(text=btn_text)  # URL в reply нет

    # Удалим None из списков (если, например, задана кнопка только на позицию 4)
    inline_keyboard = None
    reply_keyboard = None

    if inline_rows:
        inline_keyboard = InlineKeyboardMarkup()
        for r in sorted(inline_rows.keys()):
            row_buttons = [btn for btn in inline_rows[r] if btn]
            if row_buttons:
                inline_keyboard.row(*row_buttons)

    if reply_rows:
        reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for r in sorted(reply_rows.keys()):
            row_buttons = [btn for btn in reply_rows[r] if btn]
            if row_buttons:
                reply_keyboard.row(*row_buttons)

    return inline_keyboard, reply_keyboard


class Bot_Handler():
    def __init__(self) -> None:
        self.val = {}  # Инициализируем словарь для хранения переменных


    def format_message_text(self, text):
        """Форматирует текст сообщения, подставляя значения из val"""
        try:
            # Проверяем, является ли text строкой
            if not isinstance(text, str):
                return str(text)
            return text.format(val=type('DynamicValue', (), self.val))
        except KeyError as e:
            print(f"Ошибка форматирования: переменная {e} не найдена")
            return text
        except Exception as e:
            print(f"Ошибка форматирования: {e}")
            return text




    def base(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()

        # Если нужно сохранить ввод 
        # user.last_input_message_id = message['message_id']




    def start(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')
 
        user.state = state.current_state
        user.referal_url = f'https://t.me/w_vpn_v2ray_bot?start={str(user.tg_id)}'
        user.save()

        try:
            referral_id = None
            if message and message['text'].startswith("/start"):
                parts = message['text'].split()
                if len(parts) > 1:
                    referral_id = parts[1]
            if referral_id:
                if int(referral_id) == int(user.tg_id):
                    print("Пользователь не может пригласить сам себя.")
                    referral_id = None
                elif Referal.objects.filter(referred_user=user).exists():
                    print("Пользователь уже был приглашён ранее.")
                    referral_id = None
                else:
                    Referal.objects.create(
                        user=BotUser.objects.get(tg_id=referral_id),
                        referred_user=user
                    )
                    print(f"Юзер {user.tg_id} пришёл по рефке {referral_id}")
            else:
                print(f"Юзер {user.tg_id} пришёл без рефки")
            
        except Exception as e:
            print(f"Ошибка при создании реферала: {e}")

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()



    def main_menu(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')
 
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()


    def profile(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)

        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.username if user.username else 'No_username'
        self.val['user_id'] = user.tg_id
        try:
            if user.subscription:
                if user.subscription_date_end and user.subscription_date_start:
                    # Список месяцев на русском языке
                    months_ru = [
                        "января", "февраля", "марта", "апреля", "мая", "июня", 
                        "июля", "августа", "сентября", "октября", "ноября", "декабря"
                    ]

                    # Пример строки даты
                    date_start = f"{user.subscription_date_start}"

                    # Преобразуем строку в объект datetime
                    date_obj_subscription_date_start = datetime.fromisoformat(date_start)

                    # Получаем месяц в виде числа (1-12)
                    month_start = months_ru[date_obj_subscription_date_start.month - 1]

                    # Форматируем дату в нужный формат с русским месяцем
                    formatted_date_subscription_date_start = f"{date_obj_subscription_date_start.day} {month_start} {date_obj_subscription_date_start.year} года в {date_obj_subscription_date_start.strftime('%H:%M:%S')}"


                    # Пример строки даты
                    date_end = f"{user.subscription_date_end}"

                    # Преобразуем строку в объект datetime
                    date_obj_subscription_date_end = datetime.fromisoformat(date_end)

                    # Получаем месяц в виде числа (1-12)
                    month_end = months_ru[date_obj_subscription_date_end.month - 1]

                    # Форматируем дату в нужный формат с русским месяцем
                    formatted_date_subscription_date_end = f"{date_obj_subscription_date_end.day} {month_end} {date_obj_subscription_date_end.year} года в {date_obj_subscription_date_end.strftime('%H:%M:%S')}"



                    self.val['subscription_user'] = f'\n<b>Дата начала:</b> {formatted_date_subscription_date_start}\n<b>Дата окончания:</b> {formatted_date_subscription_date_end}\n' if user.subscription else 'У Вас нет подписки'
                    self.val['vpn_key'] = f'{user.vpn_key}' if user.vpn_key else 'У Вас нет ключа'
            else:
                self.val['subscription_user'] = 'У Вас нет подписки'
                self.val['vpn_key'] = 'У Вас нет ключа'
        except Exception as e:
            print('Ошибка в профиле', e)
            self.val['subscription_user'] = 'У Вас нет подписки'
            self.val['vpn_key'] = 'У Вас нет ключа'
        self.val['referal_url'] = user.referal_url if user.referal_url else f'https://t.me/w_vpn_v2ray_bot?start={str(user.tg_id)}'
        self.val['referal_money'] = (
            PaymentReferal.objects
            .filter(referal__user=user)
            .aggregate(total_amount=models.Sum('amount'))['total_amount']
            or Decimal("0.00")
        )
        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = list(Bot_Button.objects.filter(message_trigger=state).order_by('id'))
        if user.vpn_key and 'https://' in user.vpn_key:
            buttons.insert(0, Bot_Button(
                text='🚀 Подключить VPN',
                type_btn='Inline',
                type_data='url',
                data=user.vpn_key,
                button_position=1
            ))
        else:
            buttons.insert(0, Bot_Button(
                text='💳 Подписка',
                type_btn='Inline',
                type_data='data',
                data='subscription',
                button_position=1
            ))  

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)

        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()





    def subscription(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()
        

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        print('user.subscription', user.subscription)
        if user.subscription == True:
            # Список месяцев на русском языке
            months_ru = [
                "января", "февраля", "марта", "апреля", "мая", "июня", 
                "июля", "августа", "сентября", "октября", "ноября", "декабря"
            ]
            # Пример строки даты
            date_end = f"{user.subscription_date_end}"

            # Преобразуем строку в объект datetime
            date_obj_subscription_date_end = datetime.fromisoformat(date_end)

            # Получаем месяц в виде числа (1-12)
            month_end = months_ru[date_obj_subscription_date_end.month - 1]

            # Форматируем дату в нужный формат с русским месяцем
            formatted_date_subscription_date_end = f"{date_obj_subscription_date_end.day} {month_end} {date_obj_subscription_date_end.year} года {date_obj_subscription_date_end.strftime('%H:%M:%S')}"

            self.val['text'] = f'🌟 У Вас уже активна подписка до <b>{formatted_date_subscription_date_end}</b>! Вы всегда можете продлить её и продолжить пользоваться всеми преимуществами.' if user.subscription else ' '
        else:
            self.val['text'] = ' '
        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()

        # Если нужно сохранить ввод 
        # user.last_input_message_id = message['message_id']


    def support_project(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()

        # Если нужно сохранить ввод 
        # user.last_input_message_id = message['message_id']



    # START
    # Не трогать! НЕ менять
    def buy_sub(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()
        try:
            amount = callback_data.split(' ')[1]
            period = callback_data.split(' ')[2]
            limit_ip = callback_data.split(' ')[3]

            url_pay, payment_id = create_payment(
                telegram_id=user.tg_id, 
                amount=amount, 
                period=period, 
                limit_ip=limit_ip
            )
            print("url_pay", url_pay)
        except Exception as e:
            print('Ошибка в оплате', e)

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['transaction'] = payment_id
        self.val['text'] = f'Вы оплачиваете подписку на <b>W VPN</b>.\n\n<b>Период:</b> {period} мес.\n<b>Сумма к оплате:</b> {amount} руб.'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)

        inline_buttons = []
        reply_buttons = []

        inline_buttons.append(InlineKeyboardButton(text="Оплатить", url=f"{url_pay}"))

        for button in buttons:
            btn_text = translate(button.text, user.language_chooce)
            if button.type_btn == "Inline":
                if button.type_data == 'data':
                    inline_buttons.append(InlineKeyboardButton(text=btn_text, callback_data=f"{button.data} {button.text}"))
                elif button.type_data == 'url':
                    inline_buttons.append(InlineKeyboardButton(text=btn_text, url=f"{button.data}"))

            elif button.type_btn == "Reply":
                if button.type_data == 'data':
                    reply_buttons.append(KeyboardButton(text=btn_text))
                elif button.type_data == 'url':
                    inline_buttons.append(KeyboardButton(text=btn_text, url=f"{button.data}"))

        message_text = translate(text, user.language_chooce)

        # --- Отправка Inline-кнопок ---
        if inline_buttons:
            inline_keyboard = InlineKeyboardMarkup(row_width=1)
            # Разместить все inline-кнопки в одной строке (или используйте row, если нужны разные строки)
            inline_keyboard.add(*inline_buttons)

            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')

        # --- Отправка Reply-кнопок ---
        elif reply_buttons:
            reply_keyboard = ReplyKeyboardMarkup(
                resize_keyboard=True, 
                # one_time_keyboard=True
            )
            # Аналогично, все reply-кнопки в одну строку
            reply_keyboard.add(*reply_buttons)

            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')
        # Сохраняем его ID в пользовательскую модель или в state
        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        user.last_message_id = sent_message.message_id
        user.save()

        # Если нужно сохранить ввод 
        # user.last_input_message_id = message['message_id']


    def support_send(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)

        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')
        user.last_input_message_id = message['message_id']
        user.state = state.current_state
        user.save()


            

        try:
           
            summa_project = int(message['text'])  # Преобразование текста в int
            print('summa_project', summa_project)

            # Создание платежа
            url_pay, payment_id = create_payment(
                telegram_id=user.tg_id, 
                amount=str(summa_project), 
                period=0, 
                limit_ip=0
            )
            print("url_pay", url_pay, 'payment_id' , payment_id)

            # Добавляем базовые переменные
            self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
            self.val['user_id'] = user.tg_id
            self.val['summa'] = summa_project
            self.val['payment_id'] = payment_id

            # Форматируем текст с использованием переменных
            text = self.format_message_text(state.text)

            buttons = Bot_Button.objects.filter(message_trigger=state)

            inline_buttons = []
            reply_buttons = []

            # Добавляем кнопку "Оплатить"
            inline_buttons.append(InlineKeyboardButton(text="Оплатить", url=f"{url_pay}"))

            for button in buttons:
                btn_text = translate(button.text, user.language_chooce)
                if button.type_btn == "Inline":
                    if button.type_data == 'data':
                        inline_buttons.append(InlineKeyboardButton(text=btn_text, callback_data=f"{button.data} {button.text}"))
                    elif button.type_data == 'url':
                        inline_buttons.append(InlineKeyboardButton(text=btn_text, url=f"{button.data}"))

                elif button.type_btn == "Reply":
                    if button.type_data == 'data':
                        reply_buttons.append(KeyboardButton(text=btn_text))
                    elif button.type_data == 'url':
                        inline_buttons.append(KeyboardButton(text=btn_text, url=f"{button.data}"))

            message_text = translate(text, user.language_chooce)

            # --- Отправка Inline-кнопок ---
            if inline_buttons:
                inline_keyboard = InlineKeyboardMarkup(row_width=1)
                # Разместить все inline-кнопки в одной строке (или используйте row, если нужны разные строки)
                inline_keyboard.add(*inline_buttons)

                sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')

            # --- Отправка Reply-кнопок ---
            elif reply_buttons:
                reply_keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True, 
                    # one_time_keyboard=True
                )
                # Аналогично, все reply-кнопки в одну строку
                reply_keyboard.add(*reply_buttons)

                sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
            else:
                sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            try:
                if user.last_message_id:
                    bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
            except Exception as e:
                print(f'ошибка при удалении {e}')
            
            if user.last_input_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

            user.last_message_id = sent_message.message_id
            user.save()

        except ValueError as e:
            bot.send_message(chat_id=-1002304020793, text=f'У пользователя {user.tg_id} ошибка при пожертовании: {e}', parse_mode='HTML')

            inline_buttons = []
            reply_buttons = []
            # Если не число, то отправляем сообщение об ошибке и меняем state
            message_bot_message = Bot_Message.objects.get(current_state='error_support')
            buttons = Bot_Button.objects.filter(message_trigger=message_bot_message)

            for button in buttons:
                btn_text = translate(button.text, user.language_chooce)
                if button.type_btn == "Inline":
                    if button.type_data == 'data':
                        inline_buttons.append(InlineKeyboardButton(text=btn_text, callback_data=f"{button.data} {button.text}"))
                    elif button.type_data == 'url':
                        inline_buttons.append(InlineKeyboardButton(text=btn_text, url=f"{button.data}"))

                elif button.type_btn == "Reply":
                    if button.type_data == 'data':
                        reply_buttons.append(KeyboardButton(text=btn_text))
                    elif button.type_data == 'url':
                        inline_buttons.append(KeyboardButton(text=btn_text, url=f"{button.data}"))

            message_text = translate(message_bot_message.text, user.language_chooce)

            # --- Отправка Inline-кнопок ---
            if inline_buttons:
                inline_keyboard = InlineKeyboardMarkup()
                # Разместить все inline-кнопки в одной строке (или используйте row, если нужны разные строки)
                inline_keyboard.add(*inline_buttons)

                sent_message_error = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')

            # --- Отправка Reply-кнопок ---
            elif reply_buttons:
                reply_keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True, 
                    # one_time_keyboard=True
                )
                # Аналогично, все reply-кнопки в одну строку
                reply_keyboard.add(*reply_buttons)

                sent_message_error = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
            else:
                sent_message_error = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

            # sent_message_error = bot.send_message(chat_id=user.tg_id, text=message_bot_message.text, parse_mode='HTML')
            user.state = 'error_support'

            try:
                if user.last_message_id:
                    bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
            except Exception as e:
                print(f'ошибка при удалении {e}')
            
            if user.last_input_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

            user.last_message_id = sent_message_error.message_id
            user.save()
    # END





    def error_support(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()

        # Если нужно сохранить ввод 
        # user.last_input_message_id = message['message_id']


    def download(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)
        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()
    
    
    def restart_project(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        subprocess.run(
            ["supervisorctl", "restart", "all"],
            capture_output=True,
            text=True
        )
        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()


    def free_sub(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        if (
            user.trial_period == False 
            and user.subscription == False
        ):
            self.val['text'] = '🎉 Вы активировали пробный период на <b>3 дня!</b>'
            subscription_date_end = datetime.now() + timedelta(days=3)
            if user.vpn_key == None or user.vpn_key == '' or 'https://' not in user.vpn_key:
                sub_url = create_user_api(
                    username=str(user.tg_id),
                    expire=int(subscription_date_end.timestamp())
                )
            else:
                sub_url = update_user_api(
                    username=str(user.tg_id),
                    status='active',
                    expire=int(subscription_date_end.timestamp())
                )  
            user.server_chooce = 5
            user.trial_period = True
            user.vpn_key = sub_url
            user.subscription_date_start = datetime.now()
            user.subscription_date_end = subscription_date_end
            user.subscription = True

        elif user.trial_period == False and user.subscription == True:
            self.val['text'] = '🎉 Вы получили +3 дня к своей подписке!'
            user.trial_period = True
            subscription_date_end = user.subscription_date_end + timedelta(days=3)
            user.subscription_date_end = subscription_date_end
            update_user_api(
                username=str(user.tg_id),
                status='active',
                expire=int(subscription_date_end.timestamp())
            )
        else:
            self.val['text'] = 'У Вас уже был активирован пробный период.'
        user.save()
            

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = list(Bot_Button.objects.filter(message_trigger=state).order_by('id'))
        buttons.insert(0, Bot_Button(
            text='🚀 Подключить VPN',
            type_btn='Inline',
            type_data='url',
            data=user.vpn_key,
            button_position=1
        ))

        inline_keyboard, reply_keyboard = build_bot_keyboards(buttons, user.language_chooce)
        message_text = translate(text, user.language_chooce)

        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        except Exception as e:
            print(f'ошибка при удалении {e}')

        if inline_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=inline_keyboard, parse_mode='HTML')
        elif reply_keyboard:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, reply_markup=reply_keyboard, parse_mode='HTML')
        else:
            sent_message = bot.send_message(chat_id=user.tg_id, text=message_text, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()