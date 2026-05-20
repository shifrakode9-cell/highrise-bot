import os
import asyncio
import warnings
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

warnings.filterwarnings("ignore")

# 1. سيرفر الاستقرار
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online")
    def log_message(self, format, *args): return

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck)
    server.serve_forever()

# 2. كلاس البوت
class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل الآن!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.username.lower() == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        if user.username.lower() == "qais29":
            if message == "/setbotpos":
                # الطريقة الصحيحة للحصول على إحداثيات المستخدم في SDK 25
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        # نقل البوت لموقعك مباشرة دون الحاجة لـ get_bot_info
                        await self.highrise.teleport(self.bot_id, pos)
                        await self.highrise.chat("🤖 تم تثبيت موقع البوت بنجاح!")
                        break

# 3. التشغيل
async def start_bot():
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    if room_id and api_key:
        from highrise.__main__ import BotDefinition, main
        await main([BotDefinition(MyBot(), room_id, api_key)])

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    asyncio.run(start_bot())
