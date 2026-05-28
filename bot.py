import os
import asyncio
from highrise import BaseBot, Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل الآن!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تعريف البوت
    bot = MyBot()
    
    # هذه هي الطريقة الصحيحة للاتصال في SDK 25.1.0
    # نقوم بتشغيل البوت من خلال كلاس Highrise
    async with Highrise() as h:
        await h.run(bot, room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
