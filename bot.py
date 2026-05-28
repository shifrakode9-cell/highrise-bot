import os
import sys
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot

# هذا هو كود البوت الأساسي
class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")
        # البوت يرسل رسالة في الغرفة ليثبت وجوده
        await self.highrise.chat("مرحباً! البوت يعمل الآن بنجاح.")
        # البوت ينتقل للمدخل
        await self.highrise.walk_to(self.highrise.get_room_entry_way())

# هذا الجزء لإرضاء Render وفتح البورت الوهمي
def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args): return
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

if __name__ == "__main__":
    # 1. تشغيل البورت الوهمي في الخلفية
    threading.Thread(target=start_health_server, daemon=True).start()
    
    # 2. تشغيل البوت باستخدام أمر النظام لضمان التوافق
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تأكد أن اسم الملف هو bot.py ليعمل أمر bot:MyNewBot
    command = [sys.executable, "-m", "highrise", "bot:MyNewBot", room_id, api_key]
    subprocess.run(command)
