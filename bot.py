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
    
    # في النسخة 25.1.0، نستخدم فئة Highrise لتشغيل البوت كالتالي:
    bot = MyBot()
    # نمرر البوت ومعلومات الاتصال إلى دالة التنسيق
    await Highrise().login(bot, room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
