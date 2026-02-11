import time
from django.core.management.base import BaseCommand
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT
from apps.bot.models import BotUser, Text_Castom, Referal, PaymentReferal
from apps.xrey_app.models import VPNServer
from translate import translate
from django.utils import timezone
from datetime import timedelta
from telebot import TeleBot
# from outline_keys import create_new_key, delete_key
from apps.bot.bot_core import tg_bot as bot_token
from datetime import datetime, timedelta
from apps.bot.bot_core import tg_bot as bot_token_main
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
import uuid
from loguru import logger as log
import traceback


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
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
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
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
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
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
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
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'

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


class Command(BaseCommand):
    # Основной 
    Configuration.account_id = '1009645'  # Ваш идентификатор магазина
    Configuration.secret_key = 'live_B0DkWGLIp3uJ8pFhgrrSk7vtYvCkhUT03X3C_nl4KzA' # Ваш секретный ключ

    # Тестовый
    # Configuration.account_id = '1022696'  # Ваш идентификатор магазина
    # Configuration.secret_key = 'test_yDII6emg84UJKMZvRdsjMXigGQLZmEfzfk-u5Wi9Jv8'  # Ваш секретный ключ
    def worker():
        try:
            if PaymentBOT.objects.filter(status='pending').exists():
                payments = PaymentBOT.objects.filter(status='pending')
                for payment in payments:
                    payment_id: str = payment.payment_id
                    status: str = payment.status
                    period: int = int(payment.period)
                    limit_ip: int = int(payment.limit_ip)

                    # Получаем информацию о платеже по его ID
                    payment_info = Payment.find_one(payment_id)
                    
                    # Получаем статус платежа
                    payment_info_dict = payment_info.__dict__
                    status = payment_info_dict.get('_PaymentResponse__status')

                    
                    
                    if status == 'succeeded':  # Платеж успешен
                        server = VPNServer.objects.order_by("count_user").first()
                        log.info(f"Выбранный сервер: {server.id}")
                        log.success(f"Платеж №{payment.id} успешно завершен!")
                        try:
                            payment.status = 'succeeded'
                            payment.save()

                            if period == 0:
                                log.info(f"Поддержал проект")
                                send_support_project(payment.user_id)
                                return

                            
                            user = BotUser.objects.get(tg_id=payment.user_id)
                            if Referal.objects.filter(referred_user=user).exists():
                                referal_obj = Referal.objects.get(referred_user=user)
                                PaymentReferal.objects.create(
                                    referal=referal_obj,
                                    amount=round((int(payment.value)) * 0.20, 2)
                                )



                            # Use timezone-aware now
                            now = timezone.now()

                            if user.subscription == True:
                                user.subscription_date_end += timedelta(days=period*30)
                                try:
                                    create_user = session.post(
                                        "http://193.58.121.190:9001/v2ray/client/update",
                                        json={
                                            "server_id": user.server_chooce,
                                            "tg_id": user.tg_id,
                                            "enable": True,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((user.subscription_date_end).timestamp() * 1000)
                                        },
                                        timeout=5,
                                    )
                                    if create_user.status_code in (200, 201):
                                        log.info(f"{user.tg_id} 1.1) Обновлен успешно!")
                                        create_user_json = create_user.json()
                                        vpn_key = create_user_json["data"]["sub_url"]
                                        user.vpn_key = vpn_key
                                    else:
                                        log.error(f"{user.tg_id} Обновлен НЕ успешно!")
                                        log.error(create_user.text)
                                except RequestException as e:
                                    log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                                    log.error(traceback.format_exc())
                                    raise Exception("HTTP error updating VPN user")


                            if user.subscription == False and user.server_chooce is None:
                                user.subscription = True
                                user.notif_subscribe_close = False
                                user.subscription_date_start = now
                                user.subscription_date_end = now + timedelta(days=period*30)
                                user.server_chooce = server.id
                                try:
                                    create_user = session.post(
                                        "http://193.58.121.190:9001/v2ray/client/create",
                                        json={
                                            "server_id": server.id,
                                            "uuid": str(uuid.uuid4()),
                                            "tg_id": user.tg_id,
                                            "enable": True,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((now + timedelta(days=period*30)).timestamp() * 1000)
                                        },
                                        timeout=5,
                                    )
                                    if create_user.status_code in (200, 201):
                                        create_user_json = create_user.json()
                                        vpn_key = create_user_json["data"]["sub_url"]
                                        user.vpn_key = vpn_key
                                        log.info(f"{user.tg_id} 1.0) Создан успешно!")
                                except Exception as e:
                                    log.error(f"Ошибка при создании пользователя VPN: {traceback.format_exc()}")
                                    raise Exception("Ошибка при создании пользователя VPN")
                            if user.subscription == False and user.server_chooce is not None:
                                user.subscription = True
                                user.notif_subscribe_close = False
                                user.subscription_date_start = now
                                user.subscription_date_end = now + timedelta(days=period*30)
                                try:
                                    create_user = session.post(
                                        "http://193.58.121.190:9001/v2ray/client/update",
                                        json={
                                            "server_id": user.server_chooce,
                                            "tg_id": user.tg_id,
                                            "enable": True,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((now + timedelta(days=period*30)).timestamp() * 1000)
                                        },
                                        timeout=5,
                                    )
                                    
                                    log.info(f"{create_user=}")
                                    if create_user.status_code in (200, 201):
                                        log.info(f"{user.tg_id} 1.0) Обновлен успешно!")
                                        create_user_json = create_user.json()
                                        vpn_key = create_user_json["data"]["sub_url"]
                                        user.vpn_key = vpn_key
                                    else:
                                        log.error(f"{user.tg_id} Обновлен НЕ успешно!")
                                        log.error(create_user.text)
                                        raise Exception("Обновлен НЕ успешно!")
                                        
                                except RequestException as e:
                                    log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                                    log.error(traceback.format_exc())
                                    raise Exception("HTTP error updating VPN")
                            
                            user.save()
                            
                            send_success_telegram_message(payment.user_id)
                        except Exception as e:
                            log.error(f"Ошибка при обработке платежа: {e}")
                            send_error_telegram_message(payment.user_id)
                            payment.status = 'error'
                            payment.save()
                            time.sleep(1)

                        
                    elif status == 'canceled':  # Платеж отменен
                        log.info(f"Платеж №{payment.id} был отменен.")
                        payment.status = 'canceled'
                        payment.save()
                        # send_error_telegram_message(payment.user_id)


                    # elif status == 'pending':
                    #     log.info(f'Платеж №{payment.id}: Ождание оплаты')

                    time.sleep(1)
        except Exception as e:
            log.error(f"Ошибка при проверке статуса платежа: {e}")

        

        try:
            target_time = timezone.now()

            if BotUser.objects.filter(subscription=True).exists():
                users = BotUser.objects.filter(subscription=True)
                for user in users:
                    date_end = user.subscription_date_end
                    if date_end:
                        if target_time >= date_end:
                            log.info(f'Пользователь {user.tg_id} подписка закончилась!')
                            user.subscription = False
                            pyment_last = pyment_last = PaymentBOT.objects.filter(status='succeeded', user_id=user.tg_id).order_by('-created_at').first()
                            log.info(f'{pyment_last=}')
                            if pyment_last is None:
                                limit_ip = 3
                            else:
                                limit_ip = pyment_last.limit_ip
                            #Обновляем v2ray ключ

                            try:
                                # user.outline_key, user.key_id = create_new_key(name=f'{user.username} {user.tg_id}')
                                try:
                                    create_user = session.post(
                                        "http://193.58.121.190:9001/v2ray/client/update",
                                        json={
                                            "server_id": user.server_chooce,
                                            "tg_id": user.tg_id,
                                            "enable": False,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((user.subscription_date_end).timestamp() * 1000)
                                        },
                                        timeout=5,
                                    )
                                    if create_user.status_code in (200, 201):
                                        log.info(f"{user.tg_id} 1.2) Обновлен успешно!")
                                        log.info(create_user.json())
                                    else:
                                        log.error('Обновлен НЕ успешно!')
                                        log.error(create_user.text)
                                except RequestException as e:
                                    log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                                    log.error(traceback.format_exc())
                                # Выдача ключа v2ray
                                pass
                            except Exception as e:
                                log.error(f"Ошибка при обновлении: {e}")


                            # delete_key(key_id=str(user.key_id))

                            # user.key_id = None
                            # user.outline_key = None
                            # user.subscription_date_end = None
                            # user.subscription_date_start = None
                            
                            user.save()

                            if user.notif_subscribe_close == False:
                                time.sleep(1)
                                user.notif_subscribe_close = True
                                user.save()
                                send_success_notification_telegram_message(user.tg_id)


        except Exception as e:
            log.error(f"Ошибка при напоминании: {e}")
            time.sleep(5)  # Задержка на случай ошибок


    while True:
        worker()
        time.sleep(0.7)



