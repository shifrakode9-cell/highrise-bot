import os
import asyncio
from highrise import BaseBot
from highrise.models import SessionMetadata

class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # في النسخة 25، نستخدم الدالة من الكلاس مباشرة 
    # ونقوم بتمرير البوت ككائن
    bot = MyBot()
    await bot.run(room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
