import asyncio
import requests
from flask import Flask
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import time

app = Flask(__name__)

# ────────────── 설정값 ──────────────
BOT_TOKEN = "8440242757:AAG-qu-liy5KS4DmBP91T6__3sJNbLhmHpc"
CHAT_ID = 6475435809

API_ID = 31015393
API_HASH = "1d64697cb809b0b2a0898665ad351eec"
SESSION_STR = "1BVtsOGYBu6TNvAU3Blhf6fM_YHGlwGVz_VLwqhXz7NffhLdgyd06LeJ1ppAFbtky-cmybTvq8L-q3p3z1BaWccKEgKrgE0PfyZSaoJn1KkLZiBP3eozujaUFsxpbrdUrDcLWPvc7EoLx6SN7a9xBGpev4QPYPiGUpKqDMJbD8aFFoGHWA-ndju3O947qAMIkA20o9eqqJGEP9rrAkgdcpY162EqYU5c2qVUS9RSzwPwsvATBgmJPa27fJmej887wbmp48AMYtxi56QvANQcxm1En6bnCkYkuR9809aJhagiH-kAfKGcNv1XPY-L5yFsOsoXNb5-Jw3EAGOEvUUrGWOc5mdxp1MQ="

GROUP_IDS = [-1003173316990, "kyg0921"]
KEYWORDS = ["포지션 공유", "매도 하겠습니다"]

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_notification": False
    }
    for attempt in range(3):  # 3번까지 재시도
        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print("알림 전송 성공!")
                return True
        except Exception as e:
            print(f"알림 전송 실패 (시도 {attempt+1}/3): {e}")
            time.sleep(2)
    return False

async def telethon_monitor():
    while True:  # 무한 재연결 루프
        try:
            print("텔레그램 연결 시도...")
            client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
            await client.start()
            print("텔레그램 연결 성공!")
            
            @client.on(events.NewMessage(chats=GROUP_IDS))
            async def handler(event):
                text = event.raw_text
                if text:
                    matched = [kw for kw in KEYWORDS if kw in text]
                    if matched:
                        alert = f"🔥 키워드 감지: {', '.join(matched)}\n\n{text[:500]}"
                        send_alert(alert)
                        print(f"키워드 감지됨: {matched}")
            
            print(f"모니터링 중... 채널 수: {len(GROUP_IDS)}")
            await client.run_until_disconnected()
            
        except FloodWaitError as e:
            print(f"FloodWait 에러: {e.seconds}초 대기")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"연결 에러: {e}")
            print("10초 후 재연결...")
            await asyncio.sleep(10)

def run_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telethon_monitor())

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

monitor_thread = threading.Thread(target=run_telethon, daemon=True)
monitor_thread.start()
