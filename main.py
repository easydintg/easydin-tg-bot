
from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHATBASE_API_KEY = os.getenv('CHATBASE_API_KEY')
CHATBASE_BOT_ID = os.getenv('CHATBASE_BOT_ID')

TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

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

        if chatbase_response.ok:
            answer = chatbase_response.json()['messages'][0]['content']
        else:
            answer = 'Извините, что-то пошло не так 😥'

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
