import os
import asyncio
from highrise import BaseBot, BotDefinition, run

class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- البوت اتصل بنجاح بالغرفة: {session_metadata.room_id} ---")
        # لا نضع أي دالة قد تسبب خطأ، فقط نكتفي بالاتصال
        await self.highrise.chat("تم الاتصال بنجاح!")

# هذا الجزء هو الطريقة الرسمية في التحديث الأخير للتشغيل
async def main():
    bot = MyNewBot()
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # دمج تعريف البوت للتشغيل
    definition = BotDefinition(bot, room_id, api_key)
    await run(definition)

if __name__ == "__main__":
    asyncio.run(main())
