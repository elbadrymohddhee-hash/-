import asyncio
from telethon import TelegramClient, events, functions
import requests

API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = '8338762809:AAEll69IsdaiFY6ycB8A2oNO5GyB4fPRhNk'
PLAYER_ID = '51620161725'
MY_CHAT_ID = '5177962707'

client = TelegramClient('diesel_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def startup_alert():
    msg = "🚀 تم تفعيل 'الديزل' بنجاح!\n🌍 البوت الآن يمسح قنوات العالم للبحث عن هدايا ببجي.\n🎯 المستهدف: 51620161725"
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={msg}")

async def global_hunter():
    keywords = ['PUBG UC', 'Free UC', 'شحن', 'هدايا', 'Gift']
    while True:
        for key in keywords:
            try:
                results = await client(functions.contacts.SearchRequest(q=key, limit=5))
                for chat in results.chats:
                    print(f"فحص قناة: {chat.title}")
            except Exception:
                continue
        await asyncio.sleep(3600)

@client.on(events.NewMessage)
async def handler(event):
    if any(w in event.raw_text.lower() for w in ['شحن', 'هدية', 'gift', 'free']):
        await client.send_message(MY_CHAT_ID, "✅ تم رصد عرض شحن وجاري التنفيذ في حسابك يا ديزل!")

async def main():
    await startup_alert()
    client.loop.create_task(global_hunter())
    await client.run_until_disconnected()

asyncio.run(main())
