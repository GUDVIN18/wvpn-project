import time
from django.core.management.base import BaseCommand
from apps.bot.bot_core import tg_bot as bot_token
from apps.worker.models import Events
from apps.bot.models import BotUser, Bot_Commands, Bot_Message, Bot_Button
from telebot import TeleBot
from apps.worker.commands_handler import Bot_Handler
import importlib
from apps.worker.callback_handler import callback_handler



class Command(BaseCommand):
    def worker(bot):
        if Events.objects.filter(status='ACCEPTED').exists():
            states = Events.objects.filter(status='ACCEPTED')
            for event in states:
                update = event.update_data
                serialized_data = {
                    'user_id': '' ,
                    'callback_id': '' ,
                    'callback_data': '' ,
                    'message': '' ,
                }

                if 'callback_query' in update:
                    # Если есть callback_query
                    user_id = update['callback_query']['from']['id']
                    message = update['callback_query'].get('message', {})  # Сообщение может отсутствовать
                    serialized_data['callback_id'] = update['callback_query']['id']  # callback_id из Telegram
                    serialized_data['callback_data'] = update['callback_query']['data']  # Данные из callback
                    

                elif 'message' in update:
                    # Если есть сообщение
                    user_id = update['message']['from']['id'] if 'from' in update['message'] else update['message']['chat']['id']
                    message = update['message']  # Достаем сообщение
                    serialized_data['callback_id'] = None  # Нет callback_id
                    serialized_data['callback_data'] = None  # Нет callback данных

                elif 'my_chat_member' in update:
                    # Если есть обновление о статусе чата
                    user_id = update['my_chat_member']['chat']['id']
                    message = {}  # В данном случае сообщения может не быть
                    serialized_data['callback_id'] = None
                    serialized_data['callback_data'] = None

                else:
                    # Обработка непредвиденного формата обновления
                    user_id = None
                    message = {}
                    serialized_data['callback_id'] = None
                    serialized_data['callback_data'] = None

                # Вы можете использовать user_id и message дальше в логике

                # В обоих случаях сохраняем сообщение и user_id
                serialized_data['message'] = message
                serialized_data['user_id'] = user_id


                # Извлекаем данные для создания пользователя
                user_data = update.get('message', {}).get('from', {})
                if 'callback_query' in update:
                    user_data = update['callback_query']['from'] 
                    print('\n\nuser_data\n\n', user_data)

                # Создаем или получаем пользователя
                if serialized_data['user_id'] is not None:
                    try:
                        user, created = BotUser.objects.get_or_create(
                            tg_id=int(serialized_data['user_id']),
                            defaults={
                                'username': user_data.get('username'),  # Извлекаем username
                                'first_name': user_data.get('first_name'),  # Извлекаем first_name
                                'language': user_data.get('language_code'),  # Извлекаем language_code
                                'premium': user_data.get('is_premium'),  # Проверяем premium-статус
                                
                            }
                        )
                        if created:
                            print(f"Создан новый пользователь с ID {serialized_data['user_id']}")


                        if user:
                            event.user = user
                        elif created:
                            event.user = created
                        event.status = 'COMPLETED'
                        event.save()
                    except ValueError as e:
                        print(f"Ошибка преобразования user_id в int: {e}")
                else:
                    event.status = 'COMPLETED'
                    event.save()
                    continue  # Пропускаем обработку этого события



                #Кнопка
                if serialized_data['callback_data']:
                    try:
                        state=Bot_Message.objects.get(current_state=serialized_data['callback_data'].split(' ')[0])
                        print('---------------STATE из NEW_WORKER' ,state)
                        if state.handler:
                            handler_name = state.handler
                        else:
                            handler_name = 'base'

                        handler = getattr(Bot_Handler(), handler_name)
                        handler(bot, state=state, user=user, callback_data=serialized_data['callback_data'], callback_id=serialized_data['callback_id'], message=serialized_data['message'], event=event)
                    except Exception as e:
                        print('Нет привязанного сообщения!')

                #Текст
                else:
                    try:
                        
                        message_text = serialized_data['message']['text']
                        print(f'----------------------------- TEXT OR COMMAND {message_text}')
                        message_text = message_text.split(' ')
                        command = Bot_Commands.objects.filter(text=message_text[0])
                        if command.exists():
                            try:
                                command = command.first()
                                state = command.trigger
                                if state.handler:
                                    handler_name = state.handler
                                else:
                                    handler_name = 'base'

                                handler = getattr(Bot_Handler(), handler_name)
                                handler(bot, state=state, user=user, callback_data=serialized_data['callback_data'], callback_id=serialized_data['callback_id'], message=serialized_data['message'], event=event)
                            except Exception as e:
                                print('Произошла ошибка при обработке текста', e)

                        
                        else:
                            state=Bot_Message.objects.get(current_state=user.state)
                            if state.next_state:
                                state = Bot_Message.objects.get(current_state=state.next_state)
                                if state.handler:
                                    handler_name = state.handler
                                else:
                                    handler_name = 'base'

                                handler = getattr(Bot_Handler(), handler_name)
                                handler(bot, state=state, user=user, callback_data=serialized_data['callback_data'], callback_id=serialized_data['callback_id'], message=serialized_data['message'], event=event)


                            else:
                                if state.anyway_link:
                                    print(state.anyway_link)
                                    state = Bot_Message.objects.get(current_state=state.anyway_link)
                                    if state.handler:
                                        handler_name = state.handler
                                    else:
                                        handler_name = 'base'

                                    handler = getattr(Bot_Handler(), handler_name)
                                    handler(bot, state=state, user=user, callback_data=serialized_data['callback_data'], callback_id=serialized_data['callback_id'], message=serialized_data['message'], event=event)

                    except:
                        state=Bot_Message.objects.get(current_state=user.state)
                        if state.next_state:
                            state = Bot_Message.objects.get(current_state=state.next_state)
                            if state.handler:
                                handler_name = state.handler
                            else:
                                handler_name = 'base'

                            handler = getattr(Bot_Handler(), handler_name)
                            handler(bot, state=state, user=user, callback_data=serialized_data['callback_data'], callback_id=serialized_data['callback_id'], message=serialized_data['message'], event=event)

    bot = TeleBot(bot_token)
    while True:
        worker(bot)
        time.sleep(0.05)



