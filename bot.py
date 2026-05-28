import os
from highrise import BaseBot, run

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")

if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # هذه الطريقة هي المعيار الرسمي لتشغيل بوتات Highrise
    # نحن نمرر الكلاس الخاص بنا والآيدي والتوكن
    run(MyBot, room_id, api_key)
