import time
from apps.bot.models import BotUser, Text_Castom
from translate import translate
from django.utils import timezone
from datetime import timedelta
from telebot import TeleBot
from apps.bot.bot_core import tg_bot as bot_token
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger as log


session = requests.Session()

# Configure retries and backoff for flaky VPN API calls
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=1,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)
session.headers.update({"User-Agent": "V2RayAPI/1.0"})


def send_success_notification_telegram_message(user_id):
    time.sleep(3)
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    textovka = Text_Castom.objects.get(condition='send_success_notification_telegram_message')
    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = textovka.text
    else:
        text_message = translate(textovka.text, user.language_chooce)
    
    data_second = {
        "chat_id": user_id,
        "text": f"{text_message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "💳 Подписка", "callback_data": "subscription"},
                    {"text": "🏠 В главное меню", "callback_data": "main_menu"},
                ]
            ]
        }
    }
    
    response = session.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()
    
    # Получаем message_id из ответа
    message_id_new = response_json['result']['message_id']

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    log.success(f"Saved successfully! sub user.last_message_id={user.last_message_id} message_id={message_id_new}")
    
    return response_json



def send_success_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    textovka = Text_Castom.objects.get(condition='send_success_telegram_message')
    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = textovka.text
    else:
        text_message = translate(textovka.text, user.language_chooce)
    
    data_second = {
        "chat_id": user_id,
        "text": f"{text_message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "⚙️ Профиль", "callback_data": "profile"},
                    {"text": "🏠 В главное меню", "callback_data": "main_menu"},
                ]
            ]
        }
    }
    
    response = session.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()

    # Получаем message_id из ответа
    message_id_new = response_json['result']['message_id']

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    log.success(f"Saved successfully! oplata user.last_message_id={user.last_message_id} message_id={message_id_new}")
    time.sleep(1)
    return response_json







def send_support_project(user_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    textovka = Text_Castom.objects.get(condition='send_support_project')
    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = textovka.text
    else:
        text_message = translate(textovka.text, user.language_chooce)
    
    data_second = {
        "chat_id": user_id,
        "text": f"{text_message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🏠 В главное меню", "callback_data": "main_menu"},
                ]
            ]
        }
    }
    
    response = session.post(url, json=data_second, timeout=5)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()

    # Получаем message_id из ответа
    message_id_new = response_json['result']['message_id']

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    log.success(f"Saved successfully! oplata user.last_message_id={user.last_message_id} message_id={message_id_new}")
    time.sleep(1)
    return response_json






def send_error_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = "❌ Платеж не прошел!"
    else:
        text_message = translate("❌ Платеж не прошел!", user.language_chooce)
    
    data_second = {
        "chat_id": user_id,
        "text": text_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,

    }
    
    response = session.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram
