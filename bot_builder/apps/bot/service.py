import uuid
from yookassa import Configuration, Payment
from django.conf import settings
from apps.bot.models import Payment as PaymentBOT
from typing import Optional
from django.utils import timezone


def setup_yookassa():
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(
        telegram_id: int,
        amount: float,
        limit_ip: int,
        period: int,
        description: Optional[str] = None,
) -> tuple[str, int]:
    setup_yookassa()
    payment = Payment.create({
        "amount": {"value": f"{float(amount):.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/w_vpn_v2ray_bot"},
        "description": f"Оплата подписки на W VPN #{telegram_id}",
        "metadata": {
            "amount": amount,
            "limit_ip": limit_ip,
            "period": period,
            "telegram_id": str(telegram_id)
        },
        "capture": True,
    }, str(uuid.uuid4()))

    payment_obj = PaymentBOT.objects.create(
        payment_id=payment.id,
        status=payment.status,
        value=amount,
        limit_ip=limit_ip,
        period=period,
        user_id=telegram_id
    )

    return payment.confirmation.confirmation_url, payment_obj.id