import os
import asyncio
from highrise import BaseBot, Highrise
from highrise.__main__ import main as highrise_main

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

if __name__ == "__main__":
    # الطريقة الوحيدة لتشغيل الإصدار 25.1.0 هي محاكاة تنفيذ المكتبة الأساسي
    import sys
    # نمرر معلومات الغرفة والمفتاح عبر متغيرات البيئة
    # ثم نستدعي الدالة الرئيسية للمكتبة
    sys.argv = ["highrise", os.getenv("ROOM_ID"), os.getenv("API_KEY")]
    asyncio.run(highrise_main())
