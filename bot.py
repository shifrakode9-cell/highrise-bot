from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User
import os
import asyncio

class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ البوت متصل الآن بالخادم ومستعد لاستلام الأوامر!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.username.lower() == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        print(f"📥 استلمت رسالة من {user.username}: {message}") # للتحقق في اللوغات
        
        if user.username.lower() == "qais29":
            if message == "/setbotpos":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id:
                        bot_info = await self.highrise.get_bot_info()
                        await self.highrise.teleport(bot_info.user.id, pos)
                        await self.highrise.chat("🤖 تم تحديث موقع البوت بنجاح!")
                        break
            
            # يمكنك إضافة باقي الأوامر هنا بنفس الطريقة
