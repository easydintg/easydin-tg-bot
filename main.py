from flask import Flask, request
import requests
import os

app = Flask(__name__)  # <-- Этой строки не хватало

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print(">>> 🚀 Webhook вызван!")
        data = request.get_json()
        print(">>> 📥 Получен запрос:", data)

        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            print(">>> 💬 Текст от пользователя:", user_text)

            chatbase_response = requests.post(
                "https://www.chatbase.co/api/v1/chat",
                headers={
                    "Authorization": f"Bearer {CHATBASE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [{"content": user_text, "role": "user"}],
                    "chatbotId": CHATBASE_BOT_ID
                }
            )

            print(">>> 🧠 Ответ Chatbase:", chatbase_response.text)

            if chatbase_response.ok:
                response_data = chatbase_response.json()
                answer = response_data.get("text", "Извините, Chatbase не вернул текст 😕")
            else:
                answer = "Ошибка от Chatbase 😕"

            requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": answer}
            )

    except Exception as e:
        print("❌ Ошибка в webhook:", e)

    return 'ok', 200

@app.route('/')
def home():
    return '✅ Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
