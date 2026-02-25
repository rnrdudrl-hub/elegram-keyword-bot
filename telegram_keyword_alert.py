import asyncio
import requests
from flask import Flask, request
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import time
import json

app = Flask(__name__)

BOT_TOKEN = "8440242757:AAG-qu-liy5KS4DmBP91T6__3sJNbLhmHpc"
CHAT_ID = 6475435809

API_ID = 31015393
API_HASH = "1d64697cb809b0b2a0898665ad351eec"
SESSION_STR = "1BVtsOGYBu6TNvAU3Blhf6fM_YHGlwGVz_VLwqhXz7NffhLdgyd06LeJ1ppAFbtky-cmybTvq8L-q3p3z1BaWccKEgKrgE0PfyZSaoJn1KkLZiBP3eozujaUFsxpbrdUrDcLWPvc7EoLx6SN7a9xBGpev4QPYPiGUpKqDMJbD8aFFoGHWA-ndju3O947qAMIkA20o9eqqJGEP9rrAkgdcpY162EqYU5c2qVUS9RSzwPwsvATBgmJPa27fJmej887wbmp48AMYtxi56QvANQcxm1En6bnCkYkuR9809aJhagiH-kAfKGcNv1XPY-L5yFsOsoXNb5-Jw3EAGOEvUUrGWOc5mdxp1MQ="

CHANNEL_KEYWORDS = {
    -1003173316990: ["포지션 공유", "매도 하겠습니다"],
    -1003868548636: ["포지션 공유", "매도 하겠습니다"],
    -1002971986376: ["진입가", "손절가", "익절가"],
    -1003268148181: None,
}

REPEAT_CHANNELS = [-1003173316990, -1002971986376, -1003268148181]

GROUP_IDS = list(CHANNEL_KEYWORDS.keys())

unconfirmed_alerts = {}
alert_counter = 0

def send_alert_with_button(message, alert_id, need_confirm=True):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    if need_confirm:
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ 확인", "callback_data": f"confirm_{alert_id}"}
            ]]
        }
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard)
        }
    else:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("알림 전송 성공!")
            return True
    except Exception as e:
        print(f"알림 전송 실패: {e}")
    return False

def repeat_alerts():
    while True:
        time.sleep(180)
        for alert_id, data in list(unconfirmed_alerts.items()):
            print(f"미확인 알림 재전송: {alert_id}")
            send_alert_with_button(f"⚠️ 미확인 알림!\n\n{data['message']}", alert_id, True)

async def telethon_monitor():
    global alert_counter
    while True:
        try:
            print("텔레그램 연결 시도...")
            client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
            await client.start()
            print("텔레그램 연결 성공!")
            
            @client.on(events.NewMessage(chats=GROUP_IDS))
            async def handler(event):
                global alert_counter
                text = event.raw_text
                chat_id = event.chat_id
                chat_name = event.chat.title if event.chat else "Unknown"
                
                if text:
                    keywords = CHANNEL_KEYWORDS.get(chat_id, [])
                    
                    if keywords is None:
                        matched = ["모든 메시지"]
                    else:
                        matched = [kw for kw in keywords if kw in text]
                    
                    if matched:
                        alert_counter += 1
                        alert_id = alert_counter
                        message = f"🔥 키워드 감지: {', '.join(matched)}\n📢 채널: {chat_name}\n\n{text[:500]}"
                        
                        if chat_id in REPEAT_CHANNELS:
                            unconfirmed_alerts[alert_id] = {"message": message}
                            send_alert_with_button(message, alert_id, True)
                        else:
                            send_alert_with_button(message, alert_id, False)
                        
                        print(f"키워드 감지됨: {matched} (채널: {chat_name})")
            
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

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'callback_query' in data:
        callback = data['callback_query']
        callback_data = callback.get('data', '')
        
        if callback_data.startswith('confirm_'):
            alert_id = int(callback_data.replace('confirm_', ''))
            if alert_id in unconfirmed_alerts:
                del unconfirmed_alerts[alert_id]
                print(f"알림 확인됨: {alert_id}")
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                data={"callback_query_id": callback['id'], "text": "확인 완료!"}
            )
    return "OK", 200

monitor_thread = threading.Thread(target=run_telethon, daemon=True)
monitor_thread.start()

repeat_thread = threading.Thread(target=repeat_alerts, daemon=True)
repeat_thread.start()
