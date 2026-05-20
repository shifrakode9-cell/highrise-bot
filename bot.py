import os
import sys
import subprocess
import tracemalloc
import warnings

# 1. إعدادات استقرار النظام
tracemalloc.start()
warnings.filterwarnings("ignore")

# 2. إجبار تحديث المكتبة للإصدار 25.1.0
try:
    import highrise
    if hasattr(highrise, '__version__') and not highrise.__version__.startswith('25'):
        raise ImportError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "highrise-bot-sdk==25.1.0"])
    os.execv(sys.executable, ['python'] + sys.argv)

import asyncio
import random
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

# 3. سيرفر الحماية (Keep-Alive)
class SimpleKeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args): return

def run_keep_alive():
    server = HTTPServer(('0.0.0.0', 8080), SimpleKeepAliveServer)
    server.serve_forever()

# 4. كلاس البوت
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        self.prison_position = Position(0, 0, 0)
        self.spawn_position = Position(0, 0, 0)
        self.vip_position = Position(0, 0, 0)
        self.finish_position = Position(0, 0, 0)
        self.player_positions = {}
        self.prisoners = set()
        self.dance_moves = {str(i): f"dance-tiktok{i}" for i in range(1, 11)}

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل ومستعد للعمل!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.username.lower() == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        
        # تنفيذ الرقصات
        if message in self.dance_moves:
            await self.highrise.send_emote(self.dance_moves[message])
            return

        # أوامر القائد
        if user.username.lower() == "qais29":
            if message == "/setbotpos":
                bot_info = await self.highrise.get_bot_info()
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        await self.highrise.teleport(bot_info.user.id, pos)
                        await self.highrise.chat("🤖 تم تحديث موقع البوت!")
                        break
            elif message == "/setprison":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تحديد السجن.")
                        break

# 5. التشغيل
if __name__ == "__main__":
    Thread(target=run_keep_alive, daemon=True).start()
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    if room_id and api_key:
        from highrise.__main__ import BotDefinition, main
        main([BotDefinition(MyBot(), room_id, api_key)])
