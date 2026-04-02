import time
from django.core.management.base import BaseCommand
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT
from apps.bot.models import BotUser, Referal, PaymentReferal
from apps.xrey_app.models import VPNServer
from translate import translate
from django.utils import timezone
from datetime import timedelta
from requests.exceptions import RequestException
from loguru import logger as log
import traceback
from apps.bot.marzban_user_api import create_user_api, update_user_api
from apps.bot.telegram_api_message import (
    send_success_telegram_message,
    send_error_telegram_message,
    send_success_notification_telegram_message,
    send_support_project,
)
from django.db import close_old_connections
from django.db import transaction


class Command(BaseCommand):
    # Основной 
    Configuration.account_id = '1009645'  # Ваш идентификатор магазина
    Configuration.secret_key = 'live_B0DkWGLIp3uJ8pFhgrrSk7vtYvCkhUT03X3C_nl4KzA' # Ваш секретный ключ

    # Тестовый
    # Configuration.account_id = '1022696'  # Ваш идентификатор магазина
    # Configuration.secret_key = 'test_yDII6emg84UJKMZvRdsjMXigGQLZmEfzfk-u5Wi9Jv8'  # Ваш секретный ключ
    def worker():     
        try:
            target_time_now = timezone.now()
            users = list(BotUser.objects.filter(subscription=True))

            for user in users:
                date_end = user.subscription_date_end
                if not date_end:
                    continue

                time_left = date_end - target_time_now

                # =========================
                # 🔔 УВЕДОМЛЕНИЯ ДО ОКОНЧАНИЯ
                # =========================

                # 3 дня
                if timedelta(days=2, hours=20) <= time_left <= timedelta(days=3):
                    if not user.notif_3d:
                        try:
                            send_success_notification_telegram_message(
                                user.tg_id,
                                condition='send_message_3_day_before_deadline'
                            )
                            user.notif_3d = True
                            log.success(f"Уведомление за 3 дня успешно отправлено пользователю {user.tg_id}")
                        except Exception as e:
                            log.error(f"Ошибка 3d уведомления: {e}")

                # 1 день
                if timedelta(hours=20) <= time_left <= timedelta(days=1):
                    if not user.notif_1d:
                        try:
                            send_success_notification_telegram_message(
                                user.tg_id,
                                condition='send_message_1_day_before_deadline'
                            )
                            user.notif_1d = True
                            log.success(f"Уведомление за 1 день успешно отправлено пользователю {user.tg_id}")
                        except Exception as e:
                            log.error(f"Ошибка 1d уведомления: {e}")

                # 1 час
                if timedelta(minutes=30) <= time_left <= timedelta(hours=1):
                    if not user.notif_1h:
                        try:
                            send_success_notification_telegram_message(
                                user.tg_id,
                                condition='send_message_1_hour_before_deadline'
                            )
                            user.notif_1h = True
                            log.success(f"Уведомление за 1 час успешно отправлено пользователю {user.tg_id}")
                        except Exception as e:
                            log.error(f"Ошибка 1h уведомления: {e}")

                # =========================
                # ❌ ОКОНЧАНИЕ ПОДПИСКИ
                # =========================

                if target_time_now >= date_end:
                    log.info(f'Пользователь {user.tg_id} подписка закончилась!')
                    user.subscription = False

                    pyment_last = PaymentBOT.objects.filter(
                        status='succeeded',
                        user_id=user.tg_id
                    ).order_by('-created_at').first()

                    log.info(f'{pyment_last=}')

                    if pyment_last is None:
                        limit_ip = 3
                    else:
                        limit_ip = pyment_last.limit_ip

                    # 🔌 Отключаем VPN
                    try:
                        try:
                            update_user_key = update_user_api(
                                username=str(user.tg_id),
                                status="disabled",
                                expire=int(date_end.timestamp())
                            )
                        except RequestException as e:
                            log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                            log.error(traceback.format_exc())
                    except Exception as e:
                        log.error(f"Ошибка при обновлении: {e}")

                    # 🔔 Увед о завершении
                    if not user.notif_subscribe_close:
                        user.notif_subscribe_close = True
                        try:
                            send_success_notification_telegram_message(
                                user.tg_id,
                                condition='send_success_notification_telegram_message'
                            )
                            log.success(f"Уведомление об окончании подписки успешно отправлено пользователю {user.tg_id}")
                        except Exception:
                            log.error(f"Не удалось отправить увед: {user.tg_id}")

                user.save()

        except Exception as e:
            log.error(f"Ошибка при напоминании: {e}")
            time.sleep(0.5)

    while True:
        close_old_connections()
        worker()
        time.sleep(60)
