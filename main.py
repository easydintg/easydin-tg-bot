from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.getenv("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.getenv("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/')
def home():
    return 'Бот работает!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        # Отправка запроса в Chatbase
        chatbase_response = requests.post(
            "https://www.chatbase.co/api/v1/chat",
            headers={
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID  # ✅ Важно: именно chatbotId с большой I
            }
        )

        # Логирование полного ответа
        print(">>> Статус ответа Chatbase:", chatbase_response.status_code)
        print(">>> Текст ответа Chatbase:", chatbase_response.text)

        # Обработка ответа
        if chatbase_response.ok:
            try:
                data = chatbase_response.json()
                if "messages" in data and data["messages"]:
                    answer = data["messages"][0]["content"]
                else:
                    print(">>> Ответ от Chatbase не содержит messages:", data)
                    answer = "Извините, не удалось получить ответ от Chatbase 😕"
            except Exception as e:
                print("Ошибка парсинга JSON:", e)
                answer = "Ошибка обработки ответа 🤔"
        else:
            print(">>> Ошибка Chatbase:", chatbase_response.status_code, chatbase_response.text)
            answer = "Произошла ошибка при обращении к Chatbase."

        # Отправка ответа в Telegram
        requests.post(
            f'{TELEGRAM_API_URL}/sendMessage',
            json={'chat_id': chat_id, 'text': answer}
        )

    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
