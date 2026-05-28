import os
import asyncio
from highrise import BaseBot
from highrise import Highrise

# الكود الذي أرسلته أنت
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- تم الاتصال بنجاح بالغرفة: {session_metadata.room_id} ---")
        await self.highrise.chat("مرحباً! أنا أعمل الآن.")

# المشغل المباشر (يتجاوز دالة run التي تسبب المشاكل)
async def main():
    bot = Bot()
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # ربط البوت مباشرة بالاتصال
    await bot.run(room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
