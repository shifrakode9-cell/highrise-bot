import os
import asyncio
from highrise import BaseBot
from highrise.__main__ import main as highrise_main
from highrise.models import BotDefinition

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح ---")
        await self.highrise.chat("البوت متصل ويعمل!")

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # تعريف البوت وتمريره كـ definition
    bot_definition = BotDefinition(
        bot=MyBot(),
        room_id=room_id,
        api_key=api_key
    )
    
    # تشغيل المكتبة مع تمرير قائمة التعريفات
    await highrise_main([bot_definition])

if __name__ == "__main__":
    asyncio.run(main())
