from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone




class TelegramBotConfig(models.Model):
    bot_token = models.CharField(max_length=100)
    is_activ = models.BooleanField(null=False, blank=False, default=False, verbose_name="Is active")

    def __str__(self):
        return f'{self.bot_token}'

    class Meta:
        verbose_name = "Токен"
        verbose_name_plural = "Токены"


class Referal(models.Model):
    user = models.ForeignKey('BotUser', on_delete=models.CASCADE, related_name='referrals', verbose_name="Пользователь")
    referred_user = models.ForeignKey('BotUser', on_delete=models.CASCADE, related_name='referred_by', verbose_name="Реферал")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

class PaymentReferal(models.Model):
    referal = models.ForeignKey(Referal, on_delete=models.CASCADE, related_name='payments', verbose_name="Реферал")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")


class BotUser(models.Model):
    tg_id = models.BigIntegerField(unique=True, verbose_name="ID Telegram")
    first_name = models.CharField(max_length=250, verbose_name="Имя пользователя", blank=True, null=True)
    last_name = models.CharField(max_length=250, verbose_name="Фамилия пользователя", blank=True, null=True)
    username = models.CharField(max_length=250, verbose_name="Username пользователя", blank=True, null=True)
    language = models.CharField(max_length=250, verbose_name="Язык пользователя", blank=True, null=True)
    CHOOCE = ['ru', 'en']
    language_chooce = models.CharField(max_length=4, choices=[(x, x) for x in CHOOCE], verbose_name="Выбор языка", blank=True, null=True, default='ru')
    premium = models.BooleanField(verbose_name="Имеет ли пользователь премиум-аккаунт", default=False, blank=True, null=True)
    # state = models.CharField(max_length=110, choices=STATE_CHOICES, default='')
    state = models.CharField(max_length=255, help_text='Состояние')
    referal_url = models.CharField(max_length=255, help_text='Реферальная ссылка', blank=True, null=True)
    server_chooce = models.IntegerField(blank=True, null=True, help_text="Выбранный сервер")


    #Для outline
    subscription = models.BooleanField(verbose_name="Подписка на VPN", default=False, blank=True, null=True)
    subscription_date_end = models.DateTimeField(verbose_name="Дата окончания подписки", blank=True, null=True)
    subscription_date_start = models.DateTimeField(verbose_name="Дата начала подписки", blank=True, null=True)
    trial_period = models.BooleanField(verbose_name="Пробный период", default=False, blank=True, null=True)
    notif_subscribe_close = models.BooleanField(verbose_name="Уведовление о окончании подписки", default=False, blank=True, null=True)

    vpn_key = models.TextField(help_text="Ключ для vpn", blank=True, null=True)
    key_id = models.BigIntegerField(help_text="Id ключа", blank=True, null=True)
    name_key = models.CharField(max_length=255, help_text="Имя ключа", blank=True, null=True, default="#W%20VPN")

    last_message_id = models.BigIntegerField(null=True, blank=True, help_text="ID последнего отправленного сообщения с кнопками")
    last_input_message_id = models.BigIntegerField(null=True, blank=True, help_text="ID последнего отправленного сообщения без кнопок")

    def __str__(self):
        return f"user_object {self.tg_id} {self.username}"


    def save(self, *args, **kwargs):
        if not self.name_key and self.tg_id:
            self.name_key = f"#W%20VPN-{self.tg_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"






class Bot_Message(models.Model):
    text = models.TextField(verbose_name="Текст сообщения")
    current_state =  models.CharField(max_length=110, verbose_name="К какому состоянию привязана?", default=None, unique=True)
    next_state = models.CharField(max_length=255, verbose_name="Ссылка на состояние при вводе", default=None, null=True, blank=True)
    anyway_link = models.CharField(max_length=110, help_text="На какое состояние пебрасывает пользователя", null=True, blank=True, unique=True)
    handler = models.CharField(max_length=255, verbose_name="Имя функции обработчика", null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.text[:50]}... (Состояние: {self.current_state if self.current_state is not None else self.anyway_link})"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"



class Bot_Commands(models.Model):
    text = models.CharField(max_length=255, verbose_name="Текст команды")
    trigger = models.ForeignKey(Bot_Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_commands', verbose_name="Связанное сообщение")

    def __str__(self):
        return f"{self.text} (Триггер: {self.trigger})"

    class Meta:
        verbose_name = "Команду / reply кнопку"
        verbose_name_plural = "Команды / reply кнопки"




class Bot_Button(models.Model):
    text = models.CharField(max_length=255, verbose_name="Текст кнопки")
    message_trigger = models.ForeignKey(Bot_Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='message_triggered', verbose_name="Связанное сообщение")
    data = models.CharField(max_length=255, verbose_name='Данные', default='')
    CHOOCE = ['Inline', 'Reply']
    type_btn = models.CharField(max_length=20, choices=[(x, x) for x in CHOOCE], verbose_name="Тип кнопки", blank=True, null=True, default='Inline')

    CHOOCE_TYPE = ['data', 'url', 'web_app']
    type_data = models.CharField(max_length=20, choices=[(x, x) for x in CHOOCE_TYPE], verbose_name="Тип данных", blank=True, null=True, default='data')

    POSITIONS = [
        ('Первый ряд', [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]),
        ('Второй ряд', [('5', '5'), ('6', '6'), ('7', '7'), ('8', '8')]),
        ('Третий ряд', [('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')]),
        ('Четвертый ряд', [('13', '13'), ('14', '14'), ('15', '15'), ('16', '16')]),
        ('Пятый ряд', [('17', '17'), ('18', '18'), ('19', '19'), ('20', '20')]),
    ]
    button_position = models.CharField(
        max_length=3,
        choices=POSITIONS,
        verbose_name="Позиция кнопки",
        blank=True,
        null=True
    )
    def __str__(self):
        return f"{self.text} (Триггер: {self.message_trigger})"

    class Meta:
        verbose_name = "Кнопку"
        verbose_name_plural = "Кнопки"



class Text_Castom(models.Model):
    condition = models.TextField(verbose_name="Привязка")
    hint = models.TextField(verbose_name="Подсказка", null=True, blank=True)
    text = models.TextField(verbose_name="Текст")

    class Meta:
        verbose_name = "Редактор текстовок"
        verbose_name_plural = "Редактор текстовок"



class Payment(models.Model):
    payment_id = models.TextField(verbose_name="id заявки")
    status = models.CharField(max_length=255, verbose_name="статус оплаты")
    value = models.CharField(max_length=255, verbose_name="Цена", null=True, blank=True)
    user_id = models.CharField(max_length=255, verbose_name="id пользоователя")
    limit_ip = models.IntegerField(verbose_name="Кол-во устройств", null=True, blank=True)
    period = models.IntegerField(verbose_name="Срок", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)

    class Meta:
        verbose_name = "Оплату"
        verbose_name_plural = "Оплаты"



