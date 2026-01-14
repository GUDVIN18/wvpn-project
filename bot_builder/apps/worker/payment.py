import uuid
import asyncio
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT
import threading

# Настройки Юкасса
Configuration.account_id = '1009645'  # Ваш идентификатор магазина
Configuration.secret_key = 'live_B0DkWGLIp3uJ8pFhgrrSk7vtYvCkhUT03X3C_nl4KzA'  # Ваш секретный ключ

# Configuration.account_id = '1022696'  # Ваш идентификатор магазина
# Configuration.secret_key = 'test_Ao0tYxHhbWv0t_LE-iJ6IWxnaypnMEDTQ6dqJOF0DE4'  # Ваш секретный ключ

# Функция проверки статуса платежа
async def check_payment_status(payment_id):
    while True:
        try:
            # Получаем информацию о платеже по его ID
            payment_info = Payment.find_one(payment_id)
            
            # Получаем статус платежа
            payment_info_dict = payment_info.__dict__
            status = payment_info_dict.get('_PaymentResponse__status')

            print(f"Статус платежа: {status}")
            
            if status == 'succeeded':  # Платеж успешен
                print("Платеж успешно завершен!")
                break
            elif status == 'canceled':  # Платеж отменен
                print("Платеж был отменен.")
                break
            elif status == 'pending':
                print('Ождание оплаты')

            await asyncio.sleep(1)  # Задержка 1 секунда перед следующим запросом
        except Exception as e:
            print(f"Ошибка при проверке статуса платежа: {e}")
            await asyncio.sleep(5)  # Задержка на случай ошибок


def create_payment(description, value, period, limit_ip):
    try:
        payment = Payment.create({
            "amount": {
                "value": f"{value}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/w_vpn_v2ray_bot"
            },
            "capture": True,
            "description": f"{description}"
        }, uuid.uuid4())

        payment_info_dict = payment.__dict__
        payment_id = payment_info_dict.get('_PaymentResponse__id')
        status = payment_info_dict.get('_PaymentResponse__status')
        print(f"Создан новый платеж с ID: {payment_id}\nStatus: {status}")

        # Запуск асинхронной проверки статуса в отдельном потоке
        def run_check():
            asyncio.run(check_payment_status(payment_id=payment_id))
        threading.Thread(target=run_check, daemon=True).start()

        payment_obj = PaymentBOT.objects.create(
            payment_id=payment_id,
            status=status,
            value=value,
            limit_ip=limit_ip,
            period=period,
            user_id=description
        )

        confirmation_url = payment.confirmation.confirmation_url
        return confirmation_url, payment_obj.id

    except Exception as e:
        print('Проблема при создании платежа:', e)
        return None

if __name__ == "__main__":
    a = create_payment(
        description="6424595615",
        value="69",
        period="1",
        limit_ip="1"
    )
    print(a)