import asyncio
from highrise import BaseBot, Position, BotDefinition
from highrise.__main__ import main as run_highrise

# 1. إعدادات البوت (تأكد من وضعها هنا)
TOKEN = "68fb8d63608e9ca5b97457b98d2876615b1368945ff6da3a97bd71192534e6e4"
ROOM_ID = "663fdca136f32ee78399e525"

# 2. كلاس البوت
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print("🤖 البوت متصل وجاهز!")
        await self.highrise.chat("🤖 نظام Squid Game جاهز للعب!")

# 3. تشغيل البوت
if __name__ == "__main__":
    definitions = [BotDefinition(Bot(), ROOM_ID, TOKEN)]
    asyncio.run(run_highrise(definitions))
