import time
import requests
from django.core.management.base import BaseCommand
from apps.bot.models import BotUser
from translate import translate
from telebot import TeleBot
from apps.bot.bot_core import tg_bot as bot_token
from django.utils import timezone


MESSAGE_TEMPLATE = '''
🎉 Новые тарифы и подписки в <b>W VPN</b>!
Ознакомиться можно по кнопке <b>"Подписки"</b>.
'''


def send_message(user_id):
    user = BotUser.objects.get(tg_id=user_id)
    message_text = MESSAGE_TEMPLATE if user.language_chooce == 'ru' else translate(MESSAGE_TEMPLATE, user.language_chooce)

    payload = {
        "chat_id": user_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=payload)
    response.raise_for_status()
    response_json = response.json()
    time.sleep(1)
    return response_json


class Command(BaseCommand):
    help = "Рассылка"

    def handle(self, *args, **options):
        try:
            users = BotUser.objects.all()
            print(f"Найдено пользователей: {users.count()}")
            for user in users:
                try:
                    print(f"Отправка для: {user.tg_id}")
                    send_message(user_id=user.tg_id)

                except Exception as e:
                    print(f"Пропускаем {user.tg_id} {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при отправке: {e}")
            time.sleep(1)