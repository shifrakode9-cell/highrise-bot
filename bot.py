import os
import subprocess
import sys
from highrise import BaseBot

# هذا هو الكود الأساسي الذي يتحكم بتصرفات البوت
class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")
        await self.highrise.chat("مرحباً، البوت متصل!")

# هذا الجزء هو "المحرك" الذي يشغل البوت
if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # التأكد من وجود المتغيرات
    if not room_id or not api_key:
        print("خطأ: يرجى التأكد من إضافة ROOM_ID و API_KEY في إعدادات Render")
        sys.exit(1)

    # تشغيل المكتبة كعملية نظام لتجنب مشاكل الـ Import و الـ Terminal
    command = [sys.executable, "-m", "highrise", "bot:MyBot", room_id, api_key]
    subprocess.run(command)
