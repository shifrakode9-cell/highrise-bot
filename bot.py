from highrise import BaseBot, User

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- السيرفر متصل بنجاح! ---")
        await self.highrise.chat("تم الاتصال! البوت يعمل الآن.")

    async def on_chat(self, user: User, message: str) -> None:
        if message == "مشاركة":
            await self.highrise.chat(f"أهلاً {user.username}، تم تسجيلك.")
