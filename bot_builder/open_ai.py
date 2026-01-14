import openai
import time
# from config import API_CHAT_GPT_KEY
API_CHAT_GPT_KEY = ''

def interact_with_assistant(message):
    client = openai.OpenAI(api_key=API_CHAT_GPT_KEY)
    assistant_id='asst_6YFHSjLXt0N55sIAXfpJ44UF'
    try:
        thread = client.beta.threads.create()
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )
        
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for completion
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == 'completed':
                break
            time.sleep(1)
        
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
        
    except Exception as e:
        return f"Error: {str(e)}"



# # Сообщение для ассистента
# user_message = "Дмитрий Мужчина 18 лет 73 кг Массанабор Мясо, овощи Аллергии нет да, Концетрат сывороточного протеина 3 раза в неделю"

# # Взаимодействие с ассистентом
# response = interact_with_assistant(user_message)
# print(f"Ассистент ответил: {response}")
