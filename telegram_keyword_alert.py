import asyncio
import requests
from flask import Flask
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession

app = Flask(__name__)

# ────────────── 설정값 ──────────────
# Telegram Bot (알림 보내는 용)
BOT_TOKEN = "8440242757:AAG-qu-liy5KS4DmBP91T6__3sJNbLhmHpc"
CHAT_ID = 6475435809

# Telethon (그룹 메시지 읽는 용)
API_ID = 31015393
API_HASH = "1d64697cb809b0b2a0898665ad351eec"
SESSION_STR = "1BVtsOGYBu6TNvAU3Blhf6fM_YHGlwGVz_VLwqhXz7NffhLdgyd06LeJ1ppAFbtky-cmybTvq8L-q3p3z1BaWccKEgKrgE0PfyZSaoJn1KkLZiBP3eozujaUFsxpbrdUrDcLWPvc7EoLx6SN7a9xBGpev4QPYPiGUpKqDMJbD8aFFoGHWA-ndju3O947qAMIkA20o9eqqJGEP9rrAkgdcpY162EqYU5c2qVUS9RSzwPwsvATBgmJPa27fJmej887wbmp48AMYtxi56QvANQcxm1En6bnCkYkuR9809aJhagiH-kAfKGcNv1XPY-L5yFsOsoXNb5-Jw3EAGOEvUUrGWOc5mdxp1MQ="

# 모니터링할 그룹
GROUP_IDS = [-1003173316990, "@kyg0921"]

# 키워드
KEYWORDS = ["포지션 공유", "매도 하겠습니다"]

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_notification": False
    }
    try:
        requests.post(url, data=payload, timeout=10)
        print("알림 전송 성공!")
    except Exception as e:
        print(f"에러: {e}")

async def telethon_monitor():
    print("텔레그램 그룹 모니터링 시작...")
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.start()
    
    @client.on(events.NewMessage(chats=GROUP_IDS))
    async def handler(event):
        text = event.raw_text
        if text:
            matched = [kw for kw in KEYWORDS if kw in text]
            if matched:
                alert = f"🔥 키워드 감지: {', '.join(matched)}\n\n{text[:500]}"
                send_alert(alert)
                print(f"키워드 감지됨: {matched}")
    
    print("모니터링 중... (👑크립토 정보방👑)")
    await client.run_until_disconnected()

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

# 텔레그램 모니터링 스레드 시작
monitor_thread = threading.Thread(target=run_telethon, daemon=True)
monitor_thread.start()

