from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    print(">>> 🚀 Webhook вызван!")

    try:
        data = request.get_json()
        print(">>> 📥 Получен запрос:", data)

        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            print(">>> 💬 Сообщение от пользователя:", user_text)

            # Отправляем в Chatbase
            headers = {
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID
            }

            chatbase_response = requests.post("https://www.chatbase.co/api/v1/chat", headers=headers, json=payload)
            print(">>> 📡 Ответ Chatbase:", chatbase_response.status_code, chatbase_response.text)

            if chatbase_response.ok:
                cb_data = chatbase_response.json()
                if "messages" in cb_data and cb_data["messages"]:
                    answer = cb_data["messages"][0]["content"]
                else:
                    answer = "⚠️ Ответ пустой или без messages 😕"
            else:
                answer = "❌ Ошибка от Chatbase"

            # Отправляем в Telegram
            tg_response = requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": answer}
            )
            print(">>> 📬 Отправили в Telegram:", tg_response.status_code, tg_response.text)
    except Exception as e:
        print(">>> ❌ Ошибка внутри webhook:", e)

    return 'ok', 200

@app.route('/')
def index():
    return '🔥 Бот запущен и ждет сообщений!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
