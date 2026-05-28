import os
import asyncio
from highrise import BaseBot, run

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح بالغرفة: {session_metadata.room_id} ---")
        await self.highrise.chat("مرحباً! البوت يعمل.")

if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # هذه هي الطريقة الوحيدة الصحيحة لتشغيل البوت في الإصدار 25.1.0
    # الـ run تاخذ (الكلاس، الغرفة، التوكن)
    run(MyBot, room_id, api_key)
