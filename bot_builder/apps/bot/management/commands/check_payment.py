import time
from django.core.management.base import BaseCommand
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT
from apps.bot.models import BotUser, Text_Castom
from translate import translate
from django.utils import timezone
from datetime import timedelta
from telebot import TeleBot
# from outline_keys import create_new_key, delete_key
from apps.bot.bot_core import tg_bot as bot_token
from datetime import datetime, timedelta
from apps.bot.bot_core import tg_bot as bot_token_main
import requests
import uuid


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
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()
    
    # Получаем message_id из ответа
    print('response_json', response_json)
    message_id_new = response_json['result']['message_id']
    print('message_id', message_id_new)

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    print("Saved successfully! sub", 'user.last_message_id', user.last_message_id, 'message_id', message_id_new)
    
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
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()

    # Получаем message_id из ответа
    print('response_json', response_json)
    message_id_new = response_json['result']['message_id']
    print('message_id', message_id_new)

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    print("Saved successfully! oplata", 'user.last_message_id', user.last_message_id, 'message_id', message_id_new)
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
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    # Извлекаем JSON-ответ
    response_json = response.json()

    # Получаем message_id из ответа
    print('response_json', response_json)
    message_id_new = response_json['result']['message_id']
    print('message_id', message_id_new)

    if user.last_message_id:
        bot = TeleBot(bot_token)
        bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

    user.last_message_id = int(message_id_new)
    user.save()
    print("Saved successfully! oplata", 'user.last_message_id', user.last_message_id, 'message_id', message_id_new)
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
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


class Command(BaseCommand):
    # Основной 
    Configuration.account_id = '1009645'  # Ваш идентификатор магазина
    Configuration.secret_key = 'live_6H0jmbiiQVqUAKmQFQkiAfdhwmWM784_XWMu-31x45U'  # Ваш секретный ключ

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

                    print(f"Статус платежа: {status}")
                    
                    if status == 'succeeded':  # Платеж успешен
                        print(f"Платеж №{payment.id} успешно завершен!")
                        try:
                            payment.status = 'succeeded'
                            payment.save()

                            if period == 0:
                                send_support_project(payment.user_id)
                            
                            user = BotUser.objects.get(tg_id=payment.user_id)
                            now = datetime.now()
                            if user.subscription == False:
                                user.subscription = True
                                user.notif_subscribe_close = False
                                user.subscription_date_start = now
                                user.subscription_date_end = now + timedelta(days=period*30)
                                try:
                                    # user.outline_key, user.key_id = create_new_key(name=f'{user.username} {user.tg_id}')
                                    create_user = requests.post(
                                        "http://45.150.32.229:8080/v2ray/client/create",
                                        json={
                                            "server_id": 1,
                                            "uuid": str(uuid.uuid4()),
                                            "tg_id": user.tg_id,
                                            "enable": True,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((now + timedelta(days=period*30)).timestamp() * 1000)

                                        }
                                    )
                                    if create_user.status_code == 200 or create_user.status_code == 201:
                                        create_user_json = create_user.json()
                                        vpn_key = create_user_json["data"]["key"]
                                        user.vpn_key = vpn_key
                                    else:
                                        create_user = requests.post(
                                            "http://45.150.32.229:8080/v2ray/client/update",
                                            json={
                                                "server_id": 1,
                                                "tg_id": user.tg_id,
                                                "enable": True,
                                                "limit_ip": limit_ip,
                                                "expiry_time": int((now + timedelta(days=period*30)).timestamp() * 1000)
                                            }
                                        )
                                        if create_user.status_code == 200 or create_user.status_code == 201:
                                            print('Обновлен успешно!')
                                            create_user_json = create_user.json()
                                            vpn_key =  create_user_json["data"]["key"]
                                            user.vpn_key = vpn_key
                                except:
                                    raise Exception("Ошибка при создании пользователя VPN")

                            elif user.subscription == True:
                                user.subscription_date_end += timedelta(days=period*30)
                                try:
                                    # user.outline_key, user.key_id = create_new_key(name=f'{user.username} {user.tg_id}')
                                    create_user = requests.post(
                                        "http://45.150.32.229:8080/v2ray/client/update",
                                        json={
                                            "server_id": 1,
                                            "tg_id": user.tg_id,
                                            "enable": True,
                                            "limit_ip": limit_ip,
                                            "expiry_time": int((user.subscription_date_end + timedelta(days=period*30)).timestamp() * 1000)

                                        }
                                    )
                                    if create_user.status_code == 200 or create_user.status_code == 201:
                                        print('Обновлен успешно!')
                                        create_user_json = create_user.json()
                                        vpn_key =  create_user_json["data"]["key"]
                                        user.vpn_key = vpn_key
                                    else:
                                        print('Обновлен НЕ успешно!')
                                        print(create_user.text)
                                    # Выдача ключа v2ray
                                    pass
                                except Exception as e:
                                    print("Ошибка при обновлении", e)

                            user.save()
                            
                            send_success_telegram_message(payment.user_id)
                        except Exception as e:
                            print(f"Ошибка при обработке платежа: {e}")
                            send_error_telegram_message(payment.user_id)
                            payment.status = 'error'
                            payment.save()
                            time.sleep(1)

                        
                    elif status == 'canceled':  # Платеж отменен
                        print(f"Платеж №{payment.id} был отменен.")
                        payment.status = 'canceled'
                        payment.save()
                        # send_error_telegram_message(payment.user_id)


                    elif status == 'pending':
                        print(f'Платеж №{payment.id}: Ождание оплаты')

                    time.sleep(1)
        except Exception as e:
            print(f"Ошибка при проверке статуса платежа: {e}")
            time.sleep(5)  # Задержка на случай ошибок

        

        try:
            target_time = timezone.now()

            if BotUser.objects.filter(subscription=True).exists():
                users = BotUser.objects.filter(subscription=True)
                for user in users:
                    date_end = user.subscription_date_end
                    if date_end:
                        if target_time >= date_end:
                            user.subscription = False
                            #Обновляем v2ray ключ

                            try:
                                # user.outline_key, user.key_id = create_new_key(name=f'{user.username} {user.tg_id}')
                                create_user = requests.post(
                                    "http://45.150.32.229:8080/v2ray/client/update",
                                    json={
                                        "server_id": 1,
                                        "tg_id": user.tg_id,
                                        "enable": False,
                                        "limit_ip": limit_ip,
                                        "expiry_time": int((user.subscription_date_end).timestamp() * 1000)

                                    }
                                )
                                if create_user.status_code == 200 or create_user.status_code == 201:
                                        print('Обновлен успешно!')
                                        print(create_user.json())
                                else:
                                    print('Обновлен НЕ успешно!')
                                    print(create_user.text)
                                # Выдача ключа v2ray
                                pass
                            except Exception as e:
                                print("Ошибка при обновлении", e)


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
            print(f"Ошибка при напоминании: {e}")
            time.sleep(5)  # Задержка на случай ошибок


    while True:
        worker()
        time.sleep(1)



