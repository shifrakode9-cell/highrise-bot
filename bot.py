import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot, BotDefinition, run_bot

# 1. كود البوت الأساسي
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح! ---")
        await self.highrise.chat("مرحباً! البوت يعمل الآن.")

# 2. خادم الصحة
def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

# 3. التشغيل باستخدام BotDefinition (الطريقة الرسمية الأخيرة)
if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تعريف البوت
    definition = BotDefinition(Bot(), room_id, api_key)
    # التشغيل
    asyncio.run(run_bot(definition))
