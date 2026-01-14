import requests


response = requests.get(f'https://api.telegram.org/bot7502348548:AAGSAa9GTauhevbrGZROy4vYQ4bCIPWPHqQ/getUpdates')
print(response.json())