import json
from django.utils import timezone
from datetime import timedelta
import traceback
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import RequestException
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)
from apps.bot.models import Payment as PaymentBOT
from apps.xrey_app.models import VPNServer
from apps.bot.models import BotUser, Referal, PaymentReferal
from .telegram_api_message import (
    send_success_telegram_message,
    send_error_telegram_message,
    send_support_project
)
from apps.bot.marzban_user_api import create_user_api, update_user_api
from loguru import logger as log
from django.db import transaction



@method_decorator(csrf_exempt, name="dispatch")
class YookassaWebhookView(View):

    def post(self, request):
        try:
            try:
                notification = WebhookNotificationFactory().create(
                    json.loads(request.body)
                )
            except Exception as e:
                log.error(f"Webhook parse error: {e}")
                return HttpResponse(status=400)

            payment = notification.object
            user_id: int = int((payment.metadata or {}).get("telegram_id"))
            limit_ip: int = int((payment.metadata or {}).get("limit_ip"))
            period: int = int((payment.metadata or {}).get("period"))
            amount: int = int((payment.metadata or {}).get("amount"))

            with transaction.atomic():
                payment_db = PaymentBOT.objects.select_for_update().get(
                    payment_id=payment.id
                )

                if payment_db.status != 'pending':
                    log.warning(f"SKIP duplicate webhook {payment.id}")
                    return HttpResponse(status=200)

                if payment_db.status == 'pending':
                    if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                        if period == 0:
                            log.info("Поддержал проект")
                            send_support_project(user_id)

                            payment_db.status = payment.status
                            payment_db.save()

                            return HttpResponse(status=200)
                        user = BotUser.objects.get(tg_id=user_id)
                        server = VPNServer.objects.order_by("count_user").first()

                        if Referal.objects.filter(referred_user=user).exists():
                            referal_obj = Referal.objects.get(referred_user=user)
                            PaymentReferal.objects.create(
                                referal=referal_obj,
                                amount=round((int(amount)) * 0.20, 2)
                            )



                        # Use timezone-aware now
                        now = timezone.now()

                        if user.subscription == True:
                            log.info(f"УСЛОВИЕ 1: Пользователь {user.tg_id}")
                            subscription_date_end_1 = user.subscription_date_end + timedelta(days=period*30)
                            try:
                                user.subscription_date_end = subscription_date_end_1
                                update_user_key = update_user_api(
                                    username=str(user.tg_id),
                                    status="active",
                                    expire=int((subscription_date_end_1).timestamp())
                                )
                                
                                log.info(f"{user.tg_id} 1.1) Обновлен успешно!")
                                user.vpn_key = update_user_key
                            except RequestException as e:
                                log.error(f"{user.tg_id} Обновлен НЕ успешно!")
                                log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                                log.error(traceback.format_exc())
                                raise Exception("HTTP error updating VPN user")


                        if user.subscription == False and user.server_chooce is None:
                            subscription_date_end_2 = now + timedelta(days=period*30)
                            log.info(f"УСЛОВИЕ 2: Пользователь {user.tg_id}")
                            user.subscription = True
                            user.notif_subscribe_close = False
                            user.notif_3d = False
                            user.notif_1d = False
                            user.notif_1h = False
                            user.subscription_date_start = now
                            user.subscription_date_end = subscription_date_end_2
                            user.server_chooce = server.id
                            try:
                                create_user_key = create_user_api(
                                    username=str(user.tg_id),
                                    expire=int((subscription_date_end_2).timestamp())
                                )
                                user.vpn_key = create_user_key
                                log.info(f"{user.tg_id} 1.0) Создан успешно!")
                            except Exception as e:
                                log.error(f"Ошибка при создании пользователя VPN: {traceback.format_exc()}")
                                raise Exception("Ошибка при создании пользователя VPN")
                            
                        if user.subscription == False and user.server_chooce is not None:
                            log.info(f"УСЛОВИЕ 3: Пользователь {user.tg_id}")
                            subscription_date_end_3 = now + timedelta(days=period*30)
                            user.subscription = True
                            user.notif_subscribe_close = False
                            user.notif_3d = False
                            user.notif_1d = False
                            user.notif_1h = False
                            user.subscription_date_start = now
                            user.subscription_date_end = subscription_date_end_3
                            try:
                                try:
                                    un_user_key = create_user_api(
                                        username=str(user.tg_id),
                                        expire=int((subscription_date_end_3).timestamp())
                                    )
                                except Exception as e:
                                    un_user_key = update_user_api(
                                        username=str(user.tg_id),
                                        status="active",
                                        expire=int((subscription_date_end_3).timestamp())
                                    )
                                user.vpn_key = un_user_key
                                log.info(f"{user.tg_id} 1.2) Возобновил успешно!")
                            except RequestException as e:
                                log.error(f"HTTP error updating VPN user for {user.tg_id}: {e}")
                                log.error(traceback.format_exc())
                                raise Exception("HTTP error updating VPN")
                            
                        user.save()
                        send_success_telegram_message(user_id)
                    if notification.event == WebhookNotificationEventType.PAYMENT_CANCELED:
                        send_error_telegram_message(user_id)
                        
                    payment_db.status = payment.status
                    payment_db.save()
                    log.info(f"Received webhook: event={notification.event}, user_id={user_id}")

            return HttpResponse(status=200) 
        except Exception as e:
            log.error(f"Error processing webhook: {e}")
            log.error(traceback.format_exc())
            return HttpResponse(status=500)