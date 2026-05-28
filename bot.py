import os
from highrise import BaseBot

# هذا الجزء يربط الكود بالمتغيرات التي وضعتها في الـ Environment/Secrets
room_id = os.getenv("ROOM_ID")
api_key = os.getenv("API_KEY")

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح على سيرفر Render ---")
        await self.highrise.chat("مرحباً، البوت متصل الآن!")

    async def on_chat(self, user, message):
        if message == "مشاركة":
            await self.highrise.chat(f"أهلاً {user.username}، تم استلام طلبك.")

# ملاحظة: المكتبة ستقوم بالاتصال تلقائياً عند تشغيل الأمر عبر Terminal
