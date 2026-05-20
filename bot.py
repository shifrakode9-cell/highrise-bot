import os
import sys
import asyncio
import random
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

# ---------------------------------------------------------
# كود السيرفر الوهمي للبقاء حياً على سيرفر Render المجاني
# ---------------------------------------------------------
def run_dummy_server():
    port = int(os.environ.get("PORT", 8000))
    try:
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"✅ [Render Support] Dummy server is listening on port: {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Dummy server alert: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()


# ---------------------------------------------------------
# بوت لعبة Squid Game الآلي المطور
# ---------------------------------------------------------
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        self.prison_position = Position(0, 0, 0)
        self.spawn_position = Position(0, 0, 0)
        self.vip_position = Position(0, 0, 0)
        self.finish_position = Position(0, 0, 0)
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None

        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop", "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 بوت لعبة Squid Game الآلي دخل الغرفة وجاهز تماماً!")
        await self.highrise.chat("🤖 تم تشغيل نظام Squid Game المطور! أهلاً بالجميع.")

    async def on_user_join(self, user: User, position: Position) -> None:
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        username_lower = user.username.lower()
        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الغرفة تحت تصرفك الآن.")
            return
        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ عد إلى السجن يا @{user.username}!")
            if self.prison_position.x != 0:
                await asyncio.sleep(2.0)
                await self.highrise.teleport(user.id, self.prison_position)
            return
        await self.highrise.chat(f"🤖 أهلاً بك @{user.username}.. تحركك في الضوء الأحمر يعني إقصاءك! 🛑")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not hasattr(pos, 'x') or not hasattr(pos, 'z'): return
        current_x, current_z = round(pos.x, 1), round(pos.z, 1)
        username_lower = user.username.lower()
        if username_lower == "qais29": return

        if self.game_active and self.finish_position.x != 0 and username_lower not in self.prisoners:
            if ((current_x - self.finish_position.x)**2 + (current_z - self.finish_position.z)**2)**0.5 < 1.2:
                await self.highrise.chat(f"🎉 مبروك الفوز لـ @{user.username}! 🏆")
                if self.vip_position.x != 0: await self.highrise.teleport(user.id, self.vip_position)
                return

        if self.vip_position.x != 0 and username_lower not in self.prisoners:
            if ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5 < 1.5:
                await self.highrise.chat(f"🚨 منطقة الـ VIP محظورة يا @{user.username}! إلى السجن!")
                self.prisoners.add(username_lower)
                await self.highrise.teleport(user.id, self.prison_position)
                return

        if not self.game_active or self.light == "green":
            self.player_positions[user.id] = (current_x, current_z)
            return

        if self.light == "red" and username_lower not in self.prisoners:
            old_pos = self.player_positions.get(user.id)
            if old_pos:
                if ((current_x - old_pos[0]) ** 2 + (current_z - old_pos[1]) ** 2) ** 0.5 > 0.2:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 إقصاااء! @{user.username} تحرك في الضوء الأحمر!")
                    try: await self.highrise.send_emote("dance-drop", user.id)
                    except: pass
                    if self.prison_position.x != 0:
                        await asyncio.sleep(2.5)
                        await self.highrise.teleport(user.id, self.prison_position)
            else:
                self.player_positions[user.id] = (current_x, current_z)

    async def game_loop(self):
        try:
            while self.game_active:
                # 🟢 الضوء الأخضر
                self.light = "green"
                await self.highrise.chat("🟢 ضوء أخضر! تحركوا بحذر! 🏃‍♂️")
                await asyncio.sleep(random.uniform(3.0, 6.0))
                if not self.game_active: break
                
                # 🛑 الضوء الأحمر العشوائي المتكرر
                red_loops = random.choice([1, 2])
                for i in range(red_loops):
                    self.light = "red"
                    if red_loops == 2 and i == 1:
                        await self.highrise.chat("🛑 خدعة! ضوء أحمر مجدداً! قف مكاااانك! 🛑")
                    else:
                        await self.highrise.chat("🔴 ضوء أحمر! قف مكاااانك! 🛑")
                        
                    await asyncio.sleep(random.uniform(3.0, 5.0))
                    if not self.game_active: break
        except asyncio.CancelledError: pass

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        if message in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message], user.id)
            except: pass
            return

        if username_lower == "qais29":
            if message == "/setprison":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تسجيل موقع السجن!")
                        break
            elif message == "/setspawn":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.spawn_position = pos
                        await self.highrise.chat("🟩 تم تسجيل خط الانطلاق!")
                        break
            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 بدأت اللعبة تلقائياً!")
            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة.")
        else:
            if message in ["/setprison", "/setspawn", "ابدأ اللعبة", "اوقف اللعبة"]:
                await self.highrise.chat(f"❌ هذا الأمر خاص بالقائد qais29!")

# ---------------------------------------------------------
# تشغيل البوت المباشر المتوافق مع تحديثات مكتبة Highrise الجديدة
# ---------------------------------------------------------
async def run_bot():
    from highrise.client import BotApi
    from highrise.network import ConfigureRoomBot, create_connection
    
    TOKEN = "68fb8d63608e9ca5b97457b98d2876615b1368945ff6da3a97bd71192534e6e4"
    ROOM_ID = "663fdca136f32ee78399e525"
    
    bot = MyBot()
    api = BotApi(bot)
    bot.highrise = api
    
    print("🚀 جاري ربط الغرفة والاتصال بالسيرفرات الرسمية للعبة...")
    try:
        async with create_connection(TOKEN) as connection:
            configure = ConfigureRoomBot(ROOM_ID)
            await connection.send(configure)
            await api.run(connection)
    except Exception as e:
        print(f"❌ خطأ اتصال مباشر: {e}")

if __name__ == "__main__":
    asyncio.run(run_bot())
