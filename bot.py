import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot

class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح بالغرفة! ---")
        # لا نستخدم أي دالة حركة، فقط نكتفي بالاتصال لضمان عدم وجود أخطاء

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
    threading.Thread(target=start_health_server, daemon=True).start()
    
    from highrise.main import main
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    sys.argv = ["highrise", "bot:MyNewBot", room_id, api_key]
    main()
