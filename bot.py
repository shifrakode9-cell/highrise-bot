import os
import asyncio
from highrise import BaseBot, Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    # تأكد من وضع ROOM_ID و API_KEY في إعدادات Render
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    bot = MyBot()
    async with Highrise(room_id, api_key) as h:
        await h.run(bot)

if __name__ == "__main__":
    asyncio.run(main())
