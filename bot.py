import os
import asyncio
from highrise import BaseBot, Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    # استخراج البيانات من المتغيرات
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تصحيح طريقة الاستدعاء: نستخدم Highrise بدون تمرير المدخلات هنا
    bot = MyBot()
    # يتم التمرير من خلال دالة run أو عبر كائن الـ Highrise
    async with Highrise() as h:
        await h.run(bot, room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
