from highrise import BaseBot

class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- السيرفر متصل بنجاح! ---")
        await self.highrise.chat("تم الاتصال! البوت جاهز.")

    async def on_chat(self, user, message):
        if message == "مشاركة":
            await self.highrise.chat(f"أهلاً {user.username}، تم تسجيلك.")
