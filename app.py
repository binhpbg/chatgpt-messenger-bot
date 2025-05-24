from flask import Flask, request
import requests
import os
import logging
import re
import openai

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, json=payload, headers=headers)
    logging.info("📤 FB Send Response: %s %s", res.status_code, res.text)

def has_phone(text):
    # Regex kiểm tra số điện thoại Việt Nam (bắt đầu bằng 0 hoặc +84, sau đó là 9 số)
    return re.search(r'(0|\+84)\d{9}', text) is not None

def ask_gpt(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là nhân viên tư vấn bán hàng chuyên nghiệp của Phương Bình Group. "
                "Luôn hỏi khách hàng cung cấp số điện thoại có dùng Zalo để thuận tiện tư vấn. "
                "Nếu khách đã cung cấp số điện thoại rồi thì cảm ơn họ và trả lời: "
                "'Cảm ơn anh/chị, sẽ có nhân viên kinh doanh liên hệ tư vấn chi tiết trong thời gian sớm nhất!' "
                "Không hỏi lại số điện thoại nữa."
            )
        },
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # hoặc gpt-4 nếu bạn có quyền
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        logging.info("🤖 OpenAI SDK response: %s", response)
        return response.choices[0].message.content
    except Exception as e:
        logging.info("❌ OpenAI SDK error: %s", e)
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
    logging.info("📩 Nhận data từ Facebook: %s", data)
    for entry in data.get("entry", []):
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event['sender']['id']
            if 'message' in msg_event and 'text' in msg_event['message']:
                user_message = msg_event['message']['text']
                logging.info("✉️ Người dùng gửi: %s", user_message)
                # Nếu khách đã cho số điện thoại, trả lời cảm ơn luôn
                if has_phone(user_message):
                    reply = (
                        "Cảm ơn anh/chị, sẽ có nhân viên kinh doanh liên hệ tư vấn chi tiết trong thời gian sớm nhất!"
                    )
                    send_message(sender_id, reply)
                else:
                    # Chưa có số, hỏi xin số qua GPT
                    reply = ask_gpt(user_message)
                    send_message(sender_id, reply)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
