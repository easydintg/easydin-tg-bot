@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(">>> 🚀 Webhook вызван!")
        print(">>> 📥 Получен запрос:", data)

        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_text = data['message']['text']
            print(">>> 💬 Текст от пользователя:", user_text)

            # Запрос в Chatbase
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
                data = chatbase_response.json()
                answer = data.get("text", "Извините, Chatbase не вернул текст 😕")
            else:
                answer = "Ошибка от Chatbase 😕"

            # Ответ в Telegram
            requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": answer}
            )

    except Exception as e:
        print("❌ Ошибка в webhook:", e)

    return 'ok', 200
