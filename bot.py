import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, Highrise

# 1. تعريف البوت
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح! ---")
        await self.highrise.chat("مرحباً! البوت يعمل الآن.")

# 2. خادم الصحة (يمنع إغلاق البوت من قبل Render)
def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# 3. تشغيل البوت
async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    bot = Bot()
    async with Highrise(room_id, api_key) as h:
        await h.run(bot)

if __name__ == "__main__":
    # تشغيل الخادم في الخلفية
    threading.Thread(target=run_health_server, daemon=True).start()
    # تشغيل البوت
    asyncio.run(main())
