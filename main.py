from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}"
CHATBASE_API_KEY = os.getenv('CHATBASE_API_KEY')
CHATBASE_BOT_ID = os.getenv('CHATBASE_BOT_ID')


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        print(f"📨 Получено сообщение от Telegram: {user_text}")

        # Отправка в Chatbase
        chatbase_response = requests.post(
            'https://www.chatbase.co/api/v1/chat',
            headers={
                "Authorization": f"Bearer {CHATBASE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"content": user_text, "role": "user"}],
                "chatbotId": CHATBASE_BOT_ID  # ВАЖНО: исправлено на "chatbotId"
            }
        )

        print("== Chatbase ответ ==")
        print("Status code:", chatbase_response.status_code)
        print("Raw text:", chatbase_response.text)

        # Парсинг
        if chatbase_response.ok:
            try:
                chatbase_json = chatbase_response.json()
                print("📦 JSON Chatbase:", chatbase_json)

                if 'messages' in chatbase_json and len(chatbase_json['messages']) > 0:
                    answer = chatbase_json['messages'][0].get('content', '❔ Пустой ответ от Chatbase')
                else:
                    print("❌ В ответе нет 'messages'")
                    answer = "Ответ от Chatbase не содержит сообщений 😕"

            except Exception as e:
                print("⚠️ Ошибка парсинга JSON:", e)
                print("📥 Сырой ответ:", chatbase_response.text)
                answer = "Не удалось разобрать ответ 🤔"
        else:
            answer = "Извините, Chatbase вернул ошибку 😥"

        # Ответ пользователю
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={'chat_id': chat_id, 'text': answer}
        )

    return 'ok', 200


@app.route('/')
def home():
    return 'Бот работает!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
