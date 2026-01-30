import requests
import time
from flask import Flask
import threading

app = Flask(__name__)

# ────────────── 설정값 ──────────────
TOKEN = "8440242757:AAG-qu-liy5KS4DmBP91T6__3sJNbLhmHpc"
CHAT_ID = 6475435809
KEYWORDS = ["포지션 공유", "매도 하겠습니다"]

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_alert(message):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_notification": False
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("알림 전송 성공!")
        else:
            print(f"전송 실패: {response.status_code}")
    except Exception as e:
        print(f"에러: {e}")

def keyword_monitor():
    print("키워드 모니터링 시작...")
    while True:
        new_content = "포지션 공유 테스트"  # 테스트용
        
        if new_content:
            content_lower = new_content.lower()
            matched = [kw for kw in KEYWORDS if kw.lower() in content_lower]
            if matched:
                alert_text = f"🔥 키워드 감지: {', '.join(matched)}\n\n{new_content}"
                send_alert(alert_text)
        
        time.sleep(60)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# 여기가 핵심! gunicorn이 앱 로드할 때 스레드 시작
monitor_thread = threading.Thread(target=keyword_monitor, daemon=True)
monitor_thread.start()
