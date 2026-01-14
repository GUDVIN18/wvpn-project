from telebot import TeleBot
from apps.bot.models import TelegramBotConfig


def get_bot():
    if TelegramBotConfig.objects.exists() and TelegramBotConfig.objects.filter(is_activ=True).exists():
        config_token = TelegramBotConfig.objects.filter(is_activ=True).first().bot_token

        if not config_token:
            print("NO VALID TOKEN IN DB")
            return None
            
        bot = TeleBot(config_token)

        # return bot
        return config_token

tg_bot=get_bot()


