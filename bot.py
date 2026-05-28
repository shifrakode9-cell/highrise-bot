import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, run_bot

# تعريف البوت
class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح بالغرفة! ---")

# خادم الصحة الوهمي (لأجل Render)
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
    # 1. تشغيل خادم الصحة
    threading.Thread(target=start_health_server, daemon=True).start()
    
    # 2. تشغيل البوت مباشرة
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    
    print("--- محاولة بدء تشغيل البوت... ---")
    run_bot(MyNewBot(), room_id, api_key)
