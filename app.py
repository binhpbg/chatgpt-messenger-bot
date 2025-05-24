from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, json=payload, headers=headers)

def ask_gpt(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return res.json()['choices'][0]['message']['content']

# ✅ Đã sửa: Facebook webhook verification
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
    for entry in data.get("entry", []):
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event['sender']['id']
            if 'message' in msg_event and 'text' in msg_event['message']:
                user_message = msg_event['message']['text']
                reply = ask_gpt(user_message)
                send_message(sender_id, reply)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
