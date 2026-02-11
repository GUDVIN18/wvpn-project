import time
import requests
from django.core.management.base import BaseCommand
from apps.bot.models import BotUser
from translate import translate
from telebot import TeleBot
from apps.bot.bot_core import tg_bot as bot_token
from django.utils import timezone


# для тексста
MESSAGE_TEMPLATE = (
    "🗞"
)
# для фото
CAPTION_TEMPLATE = (
    "👋 <b>Привет!</b> Вышло небольшое обновление.\n\n"
    "<b>Кратко:</b>\n"
    "1️⃣ Исправлена проблема автоматических отключений\n"
    "2️⃣ TikTok / YouTube / Instagram снова работают без перебоев\n\n"
    "🔄 Чтобы обновиться, нажмите на кнопку <b>обновления подписки</b> в V2RayTun (как показано на фото).\n"
)


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


def send_photo(user_id):
    user = BotUser.objects.get(tg_id=user_id)

    caption = (
        CAPTION_TEMPLATE
        if user.language_chooce == 'ru'
        else translate(CAPTION_TEMPLATE, user.language_chooce)
    )

    with open("./media/2026-01-12-10.19.51.jpg", "rb") as photo:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendPhoto",
            data={
                "chat_id": user_id,
                "caption": caption,
                "parse_mode": "HTML",
            },
            files={"photo": photo},
            timeout=10,
        )

    response.raise_for_status()
    time.sleep(1)


class Command(BaseCommand):
    help = "Рассылка"

    def handle(self, *args, **options):
        try:
            users = BotUser.objects.all()
            # users = BotUser.objects.filter(tg_id__in=[6424595615])
            print(f"Найдено пользователей: {users.count()}")
            k = 0
            for user in users:
                try: 
                    print(f"{k}. Отправка для: {user.tg_id}")
                    
                    send_photo(user_id=user.tg_id)
                    k += 1
                except Exception as e:
                    print(f"Пропускаем {user.tg_id} {e}")
                    continue
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
            time.sleep(1)
        