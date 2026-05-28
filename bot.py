import os
import asyncio
from highrise import BaseBot
from highrise import Highrise

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # في إصدار 25.1.0، الاتصال يتم عبر دالة static تابعة للمكتبة
    bot = MyBot()
    # جرب هذا السطر بدلاً من كل ما سبق
    await bot.connect(room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
