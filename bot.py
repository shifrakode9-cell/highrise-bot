import os
import sys
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, run

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- البوت اتصل بالغرفة: {session_metadata.room_id} ---")
        # أمر دخول الغرفة
        await self.highrise.walk_to(self.highrise.get_room_entry_way())

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

if __name__ == "__main__":
    # تشغيل البورت الوهمي
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # تشغيل البوت الأساسي
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # هنا نستخدم الطريقة الرسمية للتشغيل
    run(MyBot, room_id, api_key)
