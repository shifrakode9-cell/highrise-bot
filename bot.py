import os
import sys
import subprocess
import asyncio
import warnings
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem
from highrise.__main__ import BotDefinition, main

# 1. تحديث المكتبة للإصدار 25
def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "highrise-bot-sdk==25.1.0"])
install_requirements()

warnings.filterwarnings("ignore")

# 2. سيرفر الويب للاستقرار
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online")
    def log_message(self, format, *args): return

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck)
    server.serve_forever()

# 3. كلاس البوت الشامل
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.dance_moves = {str(i): f"dance-tiktok{i}" for i in range(1, 11)}
        self.prisoners = set()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل بالكامل وجاهز للعمل!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.username.lower() == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()
        
        # أوامر الرقص
        if msg in self.dance_moves:
            await self.highrise.send_emote(self.dance_moves[msg])
            return

        # أوامر القائد
        if user.username.lower() == "qais29":
            # 1. مكان البوت
            if msg == "/setbotpos":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        await self.highrise.teleport(self.bot_id, pos)
                        await self.highrise.chat("🤖 تم تثبيت الموقع!")
                        break
            
            # 2. نظام السجن
            elif msg.startswith("/prison"):
                target = msg.split(" ")[1].replace("@", "")
                self.prisoners.add(target.lower())
                await self.highrise.chat(f"🔒 تم سجن @{target}")

            # 3. نظام الإفراج
            elif msg.startswith("/free"):
                target = msg.split(" ")[1].replace("@", "")
                self.prisoners.discard(target.lower())
                await self.highrise.chat(f"🕊️ تم الإفراج عن @{target}")

    async def on_tip(self, sender: User, item: CurrencyItem, receiver: User) -> None:
        if receiver.id == self.bot_id:
            await self.highrise.chat(f"💰 شكراً يا @{sender.username} على الـ {item.amount} جولد!")

# 4. تشغيل المتزامن
async def start_bot():
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    if room_id and api_key:
        await main([BotDefinition(MyBot(), room_id, api_key)])

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    asyncio.run(start_bot())
