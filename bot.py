import os
import asyncio
from highrise import BaseBot
from highrise.models import SessionMetadata

# تعريف الكلاس الخاص بك كما هو معتاد
class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

# التشغيل المباشر بدون تعقيدات استيراد highrise_main
if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # استخدام تعريف البوت المدمج
    # نستخدم المترجم المدمج للمكتبة بشكل مباشر
    import highrise
    highrise.run(MyBot(), room_id, api_key)
