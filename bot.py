import os
import asyncio
from highrise import BaseBot
from highrise.models import BotDefinition

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل!")

if __name__ == "__main__":
    # استخراج البيانات
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تعريف البوت وتمرير القيم الثلاث التي يطلبها الخطأ
    # (bot_class, room_id, api_key)
    bot = MyBot()
    
    # استخدام الأمر المباشر الذي تتوقعه المكتبة بناءً على الخطأ الذي ظهر
    import highrise
    highrise.main([BotDefinition(bot, room_id, api_key)])
