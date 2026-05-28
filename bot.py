import os
import asyncio
from highrise import Highrise

class MyBot:
    def __init__(self):
        self.bot = None

    async def run(self, room_id, api_key):
        bot_instance = Highrise()
        await bot_instance.login(room_id, api_key)
        await bot_instance.run()

async def main():
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    bot = MyBot()
    await bot.run(room_id, api_key)

if __name__ == "__main__":
    asyncio.run(main())
