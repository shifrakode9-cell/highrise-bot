import os
import asyncio
from highrise import BaseBot

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت دخل الغرفة الآن!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    bot = MyBot()
    # الطريقة الصحيحة للاتصال في الإصدارات الحديثة
    await bot.run(room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
