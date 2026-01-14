import requests
import time
from django.core.management.base import BaseCommand
from apps.bot.bot_core import tg_bot as bot
from apps.worker.models import Events
from apps.bot.models import BotUser
from loguru import logger as log


# class Command(BaseCommand):

#     def long_polling(token):
#         url = f"https://api.telegram.org/bot{token}/getUpdates"
#         offset = 0
#         timeout = 30

#         while True:
#             try:
#                 response = requests.get(f"{url}?offset={offset}&timeout={timeout}")
#                 result = response.json()

#                 if result["ok"]:
#                     for update in result["result"]:
#                         print(f'{update}\n\n')
#                         # Обработка обновления
#                         message = update.get("message", {})
#                         chat_id = message.get("chat", {}).get("id")
#                         text = message.get("text")
#                         username = update.get('message', {}).get('from', {}).get('username')
#                         first_name =  update.get('message', {}).get('from', {}).get('first_name')
#                         language = update.get('message', {}).get('from', {}).get('language_code')
#                         premium = update.get('message', {}).get('from', {}).get('premium')

#                         Events.objects.create(
#                             status='ACCEPTED',
#                             update_data=update
#                         )

#                         # Обновление offset для получения следующего обновления
#                         offset = update["update_id"] + 1

#                 else:
#                     print("Ошибка при получении обновлений")
#                 time.sleep(0.05)  # Небольшая задержка между запросами

#             except Exception as e:
#                 print(f"Произошла ошибка: {e}")
#                 time.sleep(1)  # Ожидание перед повторной попыткой в случае ошибки



#     while True:
#         long_polling(bot)










# class Command(BaseCommand):

#     def long_polling(token):
#         url = f"https://api.telegram.org/bot{token}/getUpdates"
#         offset = 0
#         timeout = 30

#         while True:
#             try:
#                 response = requests.get(f"{url}?offset={offset}&timeout={timeout}")
#                 result = response.json()

#                 if result["ok"]:
#                     for update in result["result"]:
#                         # Обработка обновления
#                         message = update.get("message", {})
#                         chat_id = message.get("chat", {}).get("id")
#                         text = message.get("text")
#                         user_info = message.get("from", {})
#                         user_id = user_info.get("id")  # Получаем user_id
#                         username = user_info.get("username")
#                         first_name = user_info.get("first_name")
#                         language = user_info.get("language_code")
#                         premium = user_info.get("premium")

#                         # Создаем событие с добавлением user_id
#                         Events.objects.create(
#                             status='ACCEPTED',
#                             update_data=update,
#                         )

#                         print(f'Обновление от пользователя {user_id} (username: {username}): {text}\n')

#                         # Обновляем offset для получения следующего обновления
#                         offset = update["update_id"] + 1

#                 else:
#                     print("Ошибка при получении обновлений")
#                 time.sleep(0.05)

#             except Exception as e:
#                 print(f"Произошла ошибка: {e}")
#                 time.sleep(1)

#     while True:
#         long_polling(bot)


# class Command(BaseCommand):
#     def long_polling(token):
#         url = f"https://api.telegram.org/bot{token}/getUpdates"
#         offset = 0
#         timeout = 30
#         media_groups = {}  # Хранилище для обработки media_group
#         processed_groups = set()  # Множество для отслеживания обработанных групп
#         media_group_timestamps = {}  # Для отслеживания времени последнего обновления группы

#         while True:
#             try:
#                 response = requests.get(f"{url}?offset={offset}&timeout={timeout}")
#                 result = response.json()

#                 if result["ok"]:
#                     current_time = time.time()
                    
#                     # Сначала проверяем и обрабатываем "застоявшиеся" группы
#                     groups_to_process = []
#                     for group_id in list(media_groups.keys()):
#                         # Если прошло больше 2 секунд с последнего обновления группы
#                         if current_time - media_group_timestamps.get(group_id, 0) > 2:
#                             groups_to_process.append(group_id)

#                     # Обрабатываем "застоявшиеся" группы
#                     for group_id in groups_to_process:
#                         if group_id not in processed_groups and len(media_groups[group_id]) > 0:
#                             photos = []
#                             messages = sorted(media_groups[group_id], key=lambda x: x.get('message_id', 0))
                            
#                             # Берем фото из всех сообщений группы
#                             for msg in messages[:10]:  # Ограничиваем до 10 фото
#                                 if 'photo' in msg:
#                                     # Берем самое большое фото из каждого сообщения
#                                     largest_photo = max(msg['photo'], key=lambda x: x.get('file_size', 0))
#                                     photos.append(largest_photo)

#                             if photos:  # Если есть фото для обработки
#                                 # Берем информацию о пользователе из последнего сообщения
#                                 last_message = messages[-1]
#                                 chat_id = last_message.get("chat_id")
#                                 user_info = last_message.get("user_info", {})
                                
#                                 update_data = {
#                                     "message": {
#                                         "chat": {
#                                             "id": chat_id,
#                                             "type": "private",
#                                             "username": user_info.get("username"),
#                                             "first_name": user_info.get("first_name"),
#                                         },
#                                         "date": last_message.get("date"),
#                                         "from": user_info,
#                                         "photo": photos,
#                                         "message_id": last_message.get("message_id"),
#                                         "media_group_id": group_id,
#                                     },
#                                     "update_id": last_message.get("update_id")
#                                 }

#                                 # Сохраняем событие
#                                 Events.objects.create(
#                                     status='ACCEPTED',
#                                     update_data=update_data,
#                                 )

#                                 print(f"Создано событие для группы {group_id} с {len(photos)} фото")
                                
#                                 # Отмечаем группу как обработанную и очищаем
#                                 processed_groups.add(group_id)
#                                 del media_groups[group_id]
#                                 del media_group_timestamps[group_id]

#                     # Обрабатываем новые обновления
#                     for update in result["result"]:
#                         message = update.get("message", {})
#                         chat_id = message.get("chat", {}).get("id")
#                         text = message.get("text")
#                         user_info = message.get("from", {})
#                         media_group_id = message.get("media_group_id")

#                         if media_group_id and media_group_id not in processed_groups:
#                             # Добавляем или обновляем временную метку для группы
#                             media_group_timestamps[media_group_id] = current_time
                            
#                             # Инициализируем группу, если её нет
#                             if media_group_id not in media_groups:
#                                 media_groups[media_group_id] = []

#                             # Сохраняем сообщение с дополнительной информацией
#                             message_data = {
#                                 "chat_id": chat_id,
#                                 "user_info": user_info,
#                                 "date": message.get("date"),
#                                 "message_id": message.get("message_id"),
#                                 "update_id": update["update_id"]
#                             }
                            
#                             if 'photo' in message:
#                                 message_data['photo'] = message['photo']
#                                 media_groups[media_group_id].append(message_data)

#                         elif not media_group_id:
#                             # Обработка одиночного сообщения
#                             Events.objects.create(
#                                 status='ACCEPTED',
#                                 update_data=update,
#                             )
#                             print(f'Обновление от пользователя {user_info.get("id")} (username: {user_info.get("username")}): {text}\n')

#                         # Обновляем offset
#                         offset = update["update_id"] + 1

#                 else:
#                     print("Ошибка при получении обновлений")
#                 time.sleep(0.05)

#             except Exception as e:
#                 print(f"Произошла ошибка: {e}")
#                 time.sleep(1)

#     while True:
#         long_polling(bot)


import threading

class Command(BaseCommand):
    def long_polling(token):
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        offset = 0
        timeout = 30
        media_groups = {}
        processed_groups = set()
        media_group_timestamps = {}
        
        def process_media_group(group_id, messages):
            """Вспомогательная функция для обработки медиа-группы"""
            photos = []
            messages = sorted(messages, key=lambda x: x.get('message_id', 0))
            
            # Собираем фото из всех сообщений группы
            for msg in messages[:10]:
                if 'photo' in msg:
                    largest_photo = max(msg['photo'], key=lambda x: x.get('file_size', 0))
                    photos.append(largest_photo)
            
            if photos:
                last_message = messages[-1]
                chat_id = last_message.get("chat_id")
                user_info = last_message.get("user_info", {})
                
                update_data = {
                    "message": {
                        "chat": {
                            "id": chat_id,
                            "type": "private",
                            "username": user_info.get("username"),
                            "first_name": user_info.get("first_name"),
                        },
                        "date": last_message.get("date"),
                        "from": user_info,
                        "photo": photos,
                        "message_id": last_message.get("message_id"),
                        "media_group_id": group_id,
                    },
                    "update_id": last_message.get("update_id")
                }

                Events.objects.create(
                    status='ACCEPTED',
                    update_data=update_data,
                )
                
                log.info(f"Создано событие для группы {group_id} с {len(photos)} фото")
                return True
            return False

        while True:
            try:
                current_time = time.time()
                
                # Проверяем застоявшиеся группы
                for group_id in list(media_groups.keys()):
                    if (current_time - media_group_timestamps.get(group_id, 0) > 2 and 
                        group_id not in processed_groups):
                        
                        if process_media_group(group_id, media_groups[group_id]):
                            processed_groups.add(group_id)
                            del media_groups[group_id]
                            del media_group_timestamps[group_id]
                
                # Получаем новые обновления
                response = requests.get(f"{url}?offset={offset}&timeout={timeout}")
                result = response.json()

                try:
                    if result["ok"]:
                    # if result:
                        for update in result["result"]:
                            message = update.get("message", {})
                            chat_id = message.get("chat", {}).get("id")
                            text = message.get("text")
                            user_info = message.get("from", {})
                            media_group_id = message.get("media_group_id")

                            if media_group_id and media_group_id not in processed_groups:
                                # Обновляем временную метку
                                media_group_timestamps[media_group_id] = current_time
                                
                                # Инициализируем группу
                                if media_group_id not in media_groups:
                                    media_groups[media_group_id] = []

                                # Сохраняем информацию о сообщении
                                message_data = {
                                    "chat_id": chat_id,
                                    "user_info": user_info,
                                    "date": message.get("date"),
                                    "message_id": message.get("message_id"),
                                    "update_id": update["update_id"],
                                    "photo": message.get("photo", [])  # Сохраняем фото, если есть
                                }
                                
                                media_groups[media_group_id].append(message_data)

                            elif not media_group_id:
                                # Обработка одиночного сообщения
                                Events.objects.create(
                                    status='ACCEPTED',
                                    update_data=update,
                                )
                                if update.get('callback_query', None):
                                    log.success(f"Обновление от user_id={update['callback_query']['from']['id']}\ndata={update['callback_query']['data']}\n")
                                

                            # Обновляем offset
                            offset = update["update_id"] + 1

                    else:
                        log.error("Ошибка при получении обновлений", result)
                except Exception as e:
                    log.error(e)
                time.sleep(0.05)  # Небольшая пауза между итерациями

            except Exception as e:
                log.error(f"Произошла ошибка: {e}")
                time.sleep(1)

    while True:
        long_polling(bot)