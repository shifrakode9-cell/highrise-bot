import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, Highrise

class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح! ---")
        await self.highrise.chat("مرحباً! البوت يعمل الآن.")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # الحل للـ TypeError: إنشاء الكائن أولاً، ثم الاتصال باستخدام دوال خاصة
    bot = Bot()
    h = Highrise() 
    # في النسخ الحديثة يتم تمرير البيانات لدالة الـ run وليس للـ init
    await h.run(room_id, api_key, bot)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    asyncio.run(main())
