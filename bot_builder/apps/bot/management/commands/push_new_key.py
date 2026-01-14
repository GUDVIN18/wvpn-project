import uuid
import time
import logging
import requests
from datetime import datetime
from django.utils import timezone

from django.core.management.base import BaseCommand
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from apps.bot.models import BotUser
from apps.bot.models import Payment as PaymentBOT
from apps.bot.bot_core import tg_bot as bot_token_main

# ================== LOGGING ==================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================

VPN_API_URL = "http://143.20.37.164:9001"

OLD_SERVER_ID = 3
NEW_SERVER_ID = 5

REQUEST_TIMEOUT = 20

# ================== SESSION ==================

def get_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


session = get_session()


def send_telegram_request(url, payload):
    """Обертка для отправки запросов в Telegram с обработкой ошибок"""
    try:
        response = session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API Error: {e}")
        return None

# --- ФУНКЦИИ УВЕДОМЛЕНИЙ ---

def send_success(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    user = BotUser.objects.get(tg_id=user_id)
    text_message = f'''Добрый день!\n\nИз-за усиленных блокировок РКН наш VPN на короткое время был недоступен. Мы уже перенесли сервера на новую площадку и полностью обновили инфраструктуру — соединения стали стабильнее и быстрее.\n\nСпасибо, что остаётесь с нами.\n\n🔑 <b>Ваша новая ссылка на ключ:</b> {user.vpn_key}'''
    
    data = {
        "chat_id": user_id,
        "text": text_message,
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
    resp = send_telegram_request(url, data)
    logger.info(f"Sent new key to user {resp}")



# ================== COMMAND ==================

class Command(BaseCommand):
    help = "Перенос пользователей на новый VPN сервер"

    def handle(self, *args, **options):
        self.migrate_users(
            old_server_id=OLD_SERVER_ID,
            new_server_id=NEW_SERVER_ID,
        )

    # ================== API ==================

    def create_user_on_server(
        self,
        user: BotUser,
        server_id: int,
        limit_ip: int,
        expiry_time: int,
    ) -> str:
        url = f"{VPN_API_URL}/v2ray/client/create"

        payload = {
            "server_id": server_id,
            "tg_id": user.tg_id,
            "uuid": str(uuid.uuid4()),
            "enable": bool(
                user.subscription_date_end and
                user.subscription_date_end > timezone.now()
            ),
            "limit_ip": limit_ip,
            "expiry_time": expiry_time,
        }

        response = session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("sub_url")

    # ================== MIGRATION ==================

    def migrate_users(self, old_server_id: int, new_server_id: int):

        users = BotUser.objects.filter(server_chooce=old_server_id)
        # users = BotUser.objects.filter(tg_id=6424595615)

        logger.info(f"Найдено пользователей: {users.count()}")
        logger.info(f"Перенос: {old_server_id} → {new_server_id}")

        success = 0
        failed = 0

        for user in users:
            try:
                last_payment = (
                    PaymentBOT.objects
                    .filter(status='succeeded', user_id=user.tg_id)
                    .order_by('-created_at')
                    .first()
                )

                limit_ip = last_payment.limit_ip if last_payment else 3
                expiry_time = (
                    int(user.subscription_date_end.timestamp() * 1000)
                    if user.subscription_date_end else 0
                )

                sub_url = self.create_user_on_server(
                    user=user,
                    server_id=new_server_id,
                    limit_ip=limit_ip,
                    expiry_time=expiry_time,
                )
                logger.info(f"Получен sub_url: {sub_url}")
                user.vpn_key = sub_url
                user.server_chooce = new_server_id
                user.save()

                logger.info(f"[OK] tg_id={user.tg_id}")
                success += 1
                send_success(user.tg_id)

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"[ERR] tg_id={user.tg_id} → {e}")
                failed += 1

        logger.info(f"Готово. Успешно: {success}, Ошибки: {failed}")