import os
import sys
from highrise import BaseBot
from highrise.main import main

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")

# بدلاً من تشغيله عبر الأوامر، سيعمل من خلال هذا الكود مباشرة
if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # نمرر القيم برمجياً بدلاً من سطر الأوامر
    # سنقوم بتشغيل الـ main الخاص بالمكتبة مع القيم المطلوبة
    sys.argv = ["highrise", "bot:MyBot", room_id, api_key]
    main()
