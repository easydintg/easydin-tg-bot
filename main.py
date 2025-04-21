from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHATBASE_API_KEY = os.environ.get("CHATBASE_API_KEY")
CHATBASE_BOT_ID = os.environ.get("CHATBASE_BOT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/')
def home():
    return 'Бот работает!'

@app.route('/webhook', methods=['POST'])
def webhook():
    print("🚀 Webhook вызван!")

    try:
        data = request.get_json(force=True)
        print("📥 Получен запрос от Telegram:", data)

        if 'message' in data:
            chat_id = data['message']['chat']['id']
            user_text = data['message'].get('text', '')
            print("✍️ Сообщение пользователя:", user_text)

            if not user_text:
                print("⚠️ Пустое сообщение, ответ не отправляется.")
                return 'ok', 200

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
            print("🧠 Ответ от Chatbase:", chatbase_response.status_code, chatbase_response.text)

            if chatbase_response.ok:
                response_data = chatbase_response.json()
                if "messages" in response_data and response_data["messages"]:
                    answer = response_data["messages"][0]["content"]
                else:
                    answer = "⚠️ Ответ пустой или без messages 😕"
            else:
                answer = f"❌ Ошибка от Chatbase: {chatbase_response.status_code}"

            # Отправка ответа в Telegram
            telegram_response = requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": answer}
            )
            print("📤 Ответ Telegram:", telegram_response.status_code, telegram_response.text)

    except Exception as e:
        print("❗️ Ошибка в обработке webhook:", e)

    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
