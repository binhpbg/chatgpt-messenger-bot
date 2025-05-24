from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Cấu hình OpenAI SDK
openai.api_key = OPENAI_API_KEY

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, json=payload, headers=headers)
    print("📤 FB Send Response:", res.status_code, res.text)

def ask_gpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # hoặc "gpt-4" nếu bạn có quyền truy cập
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        print("🤖 OpenAI SDK response:", response)
        return response.choices[0].message.content
    except Exception as e:
        print("❌ OpenAI SDK error:", e)
        return "Xin lỗi, tôi không thể trả lời ngay bây giờ."

@app.route("/", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Invalid verification", 403

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Nhận data từ Facebook:", data)
    for entry in data.get("entry", []):
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event['sender']['id']
            if 'message' in msg_event and 'text' in msg_event['message']:
                user_message = msg_event['message']['text']
                print("✉️ Người dùng gửi:", user_message)
                reply = ask_gpt(user_message)
                send_message(sender_id, reply)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
