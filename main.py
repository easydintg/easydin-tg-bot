from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем переменные окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(">>> 📥 Получен запрос:", data)

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        user_text = data['message']['text']
        print(">>> 💬 Сообщение от пользователя:", user_text)

        # Запрос в Chatbase
        chatbase_url = "https://www.chatbase.co/api/v1/chat"
        headers = {
            "Authorization": f"Bearer {CHATBASE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"content": user_text, "role": "user"}],
            "chatbotId": CHATBASE_BOT_ID
        }

        chatbase_response = requests.post(chatbase_url, headers=headers, json=payload)
        print(">>> 📡 Статус Chatbase:", chatbase_response.status_code)
        print(">>> 🧠 Ответ Chatbase:", chatbase_response.text)

        if chatbase_response.ok:
            try:
                data = chatbase_response.json()
                if "messages" in data and data["messages"]:
                    answer = data["messages"][0]["content"]
                else:
                    print(">>> ❌ Нет поля messages в ответе:", data)
                    answer = "Извините, не удалось получить ответ от Chatbase 😕"
            except Exception as e:
                print(">>> ❌ Ошибка парсинга JSON:", e)
                answer = "Произошла ошибка при обработке ответа 🤔"
        else:
            print(">>> ❌ Ошибка Chatbase:", chatbase_response.status_code, chatbase_response.text)
            answer = "Извините, произошла ошибка при обращении к Chatbase 😢"

        # Отправляем ответ пользователю
        telegram_response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": answer}
        )
        print(">>> ✉️ Ответ Telegram:", telegram_response.status_code, telegram_response.text)

    return 'ok', 200

@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
