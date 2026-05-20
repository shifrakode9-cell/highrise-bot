import os
import sys
import subprocess
import asyncio
import warnings

# 1. إخفاء التحذيرات وتنظيف اللوغات
warnings.filterwarnings("ignore")

# 2. تحديث المكتبة إجبارياً للإصدار 25
try:
    import highrise
    if hasattr(highrise, '__version__') and not highrise.__version__.startswith('25'):
        raise ImportError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "highrise-bot-sdk==25.1.0"])
    os.execv(sys.executable, ['python'] + sys.argv)

from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# 3. كلاس البوت
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.dance_moves = {str(i): f"dance-tiktok{i}" for i in range(1, 11)}

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل الآن بنجاح!")

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

# 4. نقطة التشغيل الرئيسية
if __name__ == "__main__":
    room_id = os.environ.get("ROOM_ID")
    api_key = os.environ.get("API_KEY")
    if room_id and api_key:
        from highrise.__main__ import BotDefinition, main
        main([BotDefinition(MyBot(), room_id, api_key)])
