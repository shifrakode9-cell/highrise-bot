import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot
from highrise.main import main

# تغيير اسم الكلاس لتجاوز الجلسات المعلقة
class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- البوت اتصل بنجاح بالغرفة: {session_metadata.room_id} ---")
        await self.highrise.walk_to(self.highrise.get_room_entry_way())

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args): return
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    # تشغيل خادم الصحة
    threading.Thread(target=start_health_server, daemon=True).start()
    
    # إعدادات التشغيل
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # التشغيل بالطريقة الرسمية الصحيحة
    sys.argv = ["highrise", "bot:MyNewBot", room_id, api_key]
    main()
