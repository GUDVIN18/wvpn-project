import requests
import time
from django.core.management.base import BaseCommand
from apps.bot.bot_core import tg_bot as bot
from apps.worker.models import Events
from apps.bot.models import BotUser
from loguru import logger as log
import subprocess


def restart_bot():
    log.error("Restarting bot via supervisor...")
    subprocess.run(["supervisorctl", "restart", "all"])

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
                # response = requests.get(f"{url}?offset={offset}&timeout={timeout}")

                try:
                    response = requests.get(
                        url,
                        params={"offset": offset, "timeout": timeout},
                        timeout=timeout + 5
                    )
                    result = response.json()

                except requests.exceptions.ChunkedEncodingError as e:
                    log.error(f"Connection closed: {e}")
                    restart_bot()
                    break

                except requests.exceptions.ConnectionError as e:
                    log.error(f"Connection error: {e}")
                    restart_bot()
                    break

                except requests.exceptions.ReadTimeout:
                    # это нормально для long polling
                    continue

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
                #time.sleep(0.05)  # Небольшая пауза между итерациями

            except Exception as e:
                log.error(f"Произошла ошибка: {e}")
                time.sleep(1)

    # while True:
    long_polling(bot)
