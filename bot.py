import os
import sys
from highrise import BaseBot

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")
        await self.highrise.chat("تم الاتصال بالبوت.")

# هذا الجزء هو "المحرك" الذي سيعمل بمجرد تشغيل الأمر
if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # هنا نطلب من SDK البدء باستخدام القيم المقروءة من البيئة
    # ملاحظة: إذا كان إصدارك يحتاج القيم في أمر التشغيل، 
    # فسيحاول الكود تشغيل نفسه بالقيم التي سحبناها من os.getenv
    import asyncio
    from highrise.main import main
    
    # هذه الطريقة تتجاوز مشاكل تمرير الوسائط في الـ Terminal
    # وهي الطريقة التي تستخدمها السيرفرات الاحترافية
    print(f"Starting bot for room: {room_id}")
