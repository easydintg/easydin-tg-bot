from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Получение переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print(">>> 🚩 Вызван webhook!")

        data = request.get_json()
        print(">>> 📥 Получен запрос:", data)

        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            print(">>> ✉️ Сообщение от пользователя:", user_text)

            # Отправка в Chatbase
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
            print(">>> 🔄 Статус Chatbase:", chatbase_response.status_code)
            print(">>> 🧠 Ответ Chatbase (raw):", chatbase_response.text)

            # Запись в файл (если print не работает)
            with open("mylog.txt", "a") as f:
                f.write(f"[{datetime.now()}] Ответ Chatbase: {chatbase_response.text}\n")

            if chatbase_response.ok:
                result = chatbase_response.json()
                if "messages" in result and result["messages"]:
                    answer = result["messages"][0]["content"]
                else:
                    answer = "Извините, не удалось получить ответ от Chatbase 😕"
            else:
                answer = "Извините, произошла ошибка при обращении к Chatbase ❗️"

            # Ответ в Telegram
            telegram_response = requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": answer}
            )
            print(">>> 📤 Ответ Telegram:", telegram_response.status_code, telegram_response.text)

    except Exception as e:
        error_msg = f">>> ❌ Ошибка в webhook: {e}"
        print(error_msg)
        with open("mylog.txt", "a") as f:
            f.write(f"[{datetime.now()}] {error_msg}\n")

    return 'ok', 200

@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
