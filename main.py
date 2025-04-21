from flask import Flask, request
import requests
import os

app = Flask(__name__)

# === Переменные окружения ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# === Webhook обработка ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        print(f"\n>>> Получено сообщение от пользователя: {user_text}")

        # Отправка в Chatbase
        chatbase_response = requests.post(
            'https://www.chatbase.co/api/v1/chat',
            headers={
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID
            }
        )

        print(f">>> Ответ от Chatbase: {chatbase_response.status_code} - {chatbase_response.text}")

        if chatbase_response.ok:
            data = chatbase_response.json()
            if "messages" in data and data["messages"]:
                answer = data["messages"][0]["content"]
            else:
                answer = "Извините, не удалось получить ответ от Chatbase 😕"
        else:
            answer = "Извините, произошла ошибка при обращении к Chatbase 😥"

        # Ответ в Telegram
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": answer}
        )

    return 'ok', 200


@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
