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
    "✅ VPN снова работает, как раньше!\n"
    "По всем вопросам писать: <b>@Dmitriy_prog</b>"
)
# для фото
CAPTION_TEMPLATE = (
    "❗️ Объявление.\n\n"
    "РКН вводит <b>новые блокировки</b>. В связи с этим, были выпущены <b>LTE конфиги</b>.\n"
    "Если у вас не появились LTE конфиги, нажмите на кнопку 'Обновить' в приложении (как показано на фото)\n\n"
    "Канал с новостями: <b>@W_VPN_PROXY</b>\n"
    "По всем вопросам писать: <b>@Dmitriy_prog</b>"
)


def send_message(user_id):
    user = BotUser.objects.get(tg_id=user_id)
    message_text = MESSAGE_TEMPLATE if user.language_chooce == 'ru' else translate(MESSAGE_TEMPLATE, user.language_chooce)

    payload = {
        "chat_id": user_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        # "reply_markup": {
        #     "inline_keyboard": [
        #         [
        #             {
        #                 "text": "🚀 Подключить VPN",
        #                 "url": f"{user.vpn_key}"
                        
        #             }
        #         ]
        #     ]
        # }
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

    with open("/personal/wvpn-project/media/2026-04-01-16.21.49.jpg", "rb") as photo:
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
                    # send_message(user_id=user.tg_id)
                    send_photo(user_id=user.tg_id)
                    k += 1
                except Exception as e:
                    print(f"Пропускаем {user.tg_id} {e}")
                    continue
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
            time.sleep(1)
        
