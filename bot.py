import asyncio
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position, BotDefinition
from highrise.__main__ import main as run_highrise

# 1. إعدادات البوت
TOKEN = "68fb8d63608e9ca5b97457b98d2876615b1368945ff6da3a97bd71192534e6e4"
ROOM_ID = "663fdca136f32ee78399e525"

# 2. كلاس البوت
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print("🤖 البوت متصل!")
        await self.highrise.chat("🤖 نظام Squid Game يعمل الآن!")

# 3. خدعة السيرفر الوهمي (تنهي مشكلة Port scan timeout)
def start_dummy_port():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"✅ المنفذ {port} مفتوح ومتاح لـ Render")
    server.serve_forever()

# 4. التشغيل
if __name__ == "__main__":
    # تشغيل السيرفر الوهمي في خيط (Thread) منفصل
    threading.Thread(target=start_dummy_port, daemon=True).start()
    
    # تشغيل البوت
    definitions = [BotDefinition(Bot(), ROOM_ID, TOKEN)]
    asyncio.run(run_highrise(definitions))
