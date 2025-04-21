from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📩 Получен update от Telegram:", data)

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')
        print("✉️ Сообщение от пользователя:", user_text)

        # Запрос к Chatbase
        chatbase_response = requests.post(
            "https://www.chatbase.co/api/v1/chat",
            headers={
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID  # 👈 Исправлено: было chatbot_id
            }
        )

        print("🔄 Статус Chatbase:", chatbase_response.status_code)
        print("📥 Ответ Chatbase:", chatbase_response.text)

        if chatbase_response.ok:
            try:
                answer = chatbase_response.json()['messages'][0]['content']
            except Exception as e:
                print("⚠️ Ошибка парсинга ответа Chatbase:", e)
                answer = "Не удалось разобрать ответ 🤔"
        else:
            answer = "Извините, что-то пошло не так 😥"

        # Ответ в Telegram
        telegram_response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={'chat_id': chat_id, 'text': answer}
        )

        print("📤 Ответ Telegram:", telegram_response.status_code, telegram_response.text)

    return 'ok', 200

@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
