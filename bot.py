import os
import asyncio
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User
from highrise.__main__ import BotDefinition, main
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. سيرفر ويب بسيط لإرضاء ريندر (لن يغلق التطبيق بعد الآن)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck)
    server.serve_forever()

# 2. كلاس البوت
class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل الآن بنجاح!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.username.lower() == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        if user.username.lower() == "qais29":
            if message == "/setbotpos":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        bot_info = await self.highrise.get_bot_info()
                        await self.highrise.teleport(bot_info.user.id, pos)
                        await self.highrise.chat("🤖 تم تحديث موقع البوت!")
                        break

# 3. التشغيل المزدوج (السيرفر + البوت)
if __name__ == "__main__":
    # تشغيل سيرفر الويب في خلفية (ليظل ريندر سعيداً)
    Thread(target=run_server, daemon=True).start()
    
    # تشغيل البوت
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    if room_id and api_key:
        main([BotDefinition(MyBot(), room_id, api_key)])
