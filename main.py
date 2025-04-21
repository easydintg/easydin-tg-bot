from flask import Flask, request
import requests
import os

app = Flask(__name__)

# === Настройки ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# === Webhook ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        # Отправка в Chatbase
        chatbase_response = requests.post(
            'https://www.chatbase.co/api/v1/chat',
            headers={
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            },
                    json={
            "messages": [{"content": user_text, "role": "user"}],
            "chatbot_id": CHATBASE_BOT_ID
        }
    )

    print(">>> Chatbase status:", chatbase_response.status_code)
    print(">>> Chatbase raw response:", chatbase_response.text)
    print("== Chatbase ответ ==")
        print(chatbase_response.status_code)
        print(chatbase_response.text)

        if chatbase_response.ok:
            try:
                answer = chatbase_response.json()['messages'][0]['content']
            except Exception as e:
                print("Ошибка парсинга ответа:", e)
                answer = 'Не удалось разобрать ответ 🤔'
        else:
            answer = 'Извините, что-то пошло не так 😥'

        # Ответ пользователю в Telegram
        requests.post(
            f'{TELEGRAM_API_URL}/sendMessage',
            json={'chat_id': chat_id, 'text': answer}
        )

    return 'ok', 200


@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
