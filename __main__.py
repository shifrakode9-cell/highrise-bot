import asyncio
from bot import MyBot, main, BotDefinition

TOKEN = "68fb8d63608e9ca5b97457b98d2876615b1368945ff6da3a97bd71192534e6e4"
ROOM_ID = "663fdca136f32ee78399e525"

definitions = [BotDefinition(MyBot(), ROOM_ID, TOKEN)]
asyncio.run(main(definitions))
