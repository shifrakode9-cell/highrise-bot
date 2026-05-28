import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, run
import asyncio

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- البوت اتصل بنجاح بالغرفة: {session_metadata.room_id} ---")
        # التحرك لمدخل الغرفة
        await self.highrise.walk_to(self.highrise.get_room_entry_way())

def start_health_server():
    # بورت وهمي لإرضاء Render
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")
        def log_message(self, format, *args): return # لإخفاء رسائل البورت المزعجة
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    # تشغيل خادم الصحة
    threading.Thread(target=start_health_server, daemon=True).start()
    
    # تشغيل البوت مع معالجة الأخطاء
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    try:
        run(MyBot, room_id, api_key)
    except Exception as e:
        print(f"خطأ أثناء الاتصال: {e}")
        # إذا حدث خطأ تسجيل دخول، ننتظر قليلاً ثم ننهي العملية ليقوم Render بإعادة تشغيل نظيفة
        import time
        time.sleep(10)
        sys.exit(1)
