import os
import asyncio
from highrise import BaseBot, Highrise

# هذا هو كود البوت الخاص بك
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح بالغرفة: {session_metadata.room_id} ---")
        await self.highrise.chat("مرحباً! البوت يعمل الآن.")

# هذه هي الطريقة الرسمية للتشغيل التي تضمن عدم وجود خطأ "AttributeError"
async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    bot = Bot()
    # نستخدم Highrise للاتصال، وليس البوت نفسه
    async with Highrise(room_id, api_key) as h:
        await h.run(bot)

if __name__ == "__main__":
    asyncio.run(main())
