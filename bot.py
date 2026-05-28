import os
import asyncio
from highrise import BaseBot

# محاولة استيراد BotDefinition من المسارين المحتملين
try:
    from highrise.models import BotDefinition
except ImportError:
    try:
        from highrise import BotDefinition
    except ImportError:
        # في حال لم ينجح أي منهما، سنقوم بتعريفه يدوياً كـ Dictionary 
        # لأن بعض إصدارات SDK 25 تستخدم القوائم مباشرة
        BotDefinition = None

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    bot = MyBot()

    import highrise
    
    # محاولة التشغيل بناءً على توفر الكلاس
    if BotDefinition:
        highrise.main([BotDefinition(bot, room_id, api_key)])
    else:
        # الطريقة البديلة في حال كان الـ SDK يستخدم مصفوفة مباشرة
        highrise.main([(bot, room_id, api_key)])
