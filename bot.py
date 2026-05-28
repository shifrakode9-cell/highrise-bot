import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, Highrise

class MyNewBot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- تم الاتصال بنجاح بالغرفة: {session_metadata.room_id} ---")

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args): return
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

async def main():
    bot = MyNewBot()
    room_id = os.getenv("ROOM_ID")
    token = os.getenv("API_KEY")
    
    # الاتصال المباشر عبر الكلاس الرسمي
    async with Highrise(room_id, token) as h:
        await h.run(bot)

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    asyncio.run(main())
