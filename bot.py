import os
import asyncio
from highrise import BaseBot, Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل الآن!")

async def main():
    # استدعاء البيانات من الإعدادات
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # 1. إنشاء كائن البوت
    bot = MyBot()
    
    # 2. إنشاء كائن الاتصال (بدون async with)
    h = Highrise()
    
    # 3. تشغيل الاتصال
    await h.run(bot, room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
