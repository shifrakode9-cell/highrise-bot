import os
from highrise import BaseBot, run

# --- هذا هو الكود الذي أرسلته أنت ---
class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print(f"--- اتصل البوت بنجاح بالغرفة: {session_metadata.room_id} ---")
        await self.highrise.chat("مرحباً! البوت يعمل الآن.")

    async def on_chat(self, user, message):
        print(f"[CHAT] {user.username}: {message}")

# --- هذا هو "المحرك" المفقود لتشغيل الكود ---
if __name__ == "__main__":
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    
    # هذه الدالة هي الطريقة الرسمية الوحيدة لتشغيل الكلاس
    run(Bot, room_id, api_key)
