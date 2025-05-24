HƯỚNG DẪN TRIỂN KHAI BOT CHATGPT + FACEBOOK MESSENGER (Python)

1. Đăng ký tài khoản https://render.com
2. Tạo Web Service mới, chọn 'Upload .zip'
3. Upload gói zip này
4. Cấu hình:
   - Build command: pip install -r requirements.txt
   - Start command: python app.py
   - Env Vars:
       - VERIFY_TOKEN = (token bạn tự đặt)
       - PAGE_ACCESS_TOKEN = (lấy từ Facebook App > Messenger > Token)
       - OPENAI_API_KEY = (lấy từ https://platform.openai.com/account/api-keys)
5. Lấy link Render (https://...onrender.com/) và cấu hình webhook trong Facebook App