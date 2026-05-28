import os
import asyncio
from highrise import BaseBot, Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # الطريقة الصحيحة للتشغيل في إصدار 25.1.0
    # نستخدم الدالة run_bot من كلاس Highrise مباشرة
    bot = MyBot()
    await Highrise().run_bot(bot, room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
