from flask import Flask, request
import requests
import os
import sys

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("\n>>> 🚀 Webhook вызван!")
        sys.stdout.flush()

        data = request.get_json()
        print(f">>> 📥 Получен запрос: {data}")
        sys.stdout.flush()

        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']

            payload = {
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID
            }
            headers = {
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post("https://www.chatbase.co/api/v1/chat", headers=headers, json=payload)
            print(f">>> 📡 Ответ Chatbase: {response.status_code} {response.text}")
            sys.stdout.flush()

            if response.ok:
                chatbase_data = response.json()
                if "messages" in chatbase_data and chatbase_data["messages"]:
                    answer = chatbase_data["messages"][0]["content"]
                else:
                    answer = "Извините, не удалось получить ответ от Chatbase 😕"
            else:
                answer = "Извините, произошла ошибка при обращении к Chatbase 😥"

            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": answer})
        else:
            print(">>> ⚠️ Нет текста в сообщении.")
            sys.stdout.flush()

    except Exception as e:
        print(f">>> ❌ Ошибка в webhook: {e}")
        sys.stdout.flush()

    return 'ok', 200

@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
