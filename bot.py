import asyncio
import random
import os
import sys
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات افتراضية - سيتم تحديثها فوراً عندما تكتب الأوامر
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None

        # الـ 10 رقصات
        self.dance_moves = {
            "1": "dance-tiktok8",
            "2": "dance-russian",
            "3": "dance-weird",
            "4": "dance-shoppingcart",
            "5": "dance-praise",
            "6": "emote-think",
            "7": "emote-wave",
            "8": "dance-blackpink",
            "9": "dance-drop",
            "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🚀 البوت متصل الآن داخل الغرفة وجاهز لاستقبال أوامرك يا قيس!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        username_lower = user.username.lower()

        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! حدد خط البداية والنهاية الآن، أنا بانتظارك.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ عد إلى مكانك يا @{user.username}!")
            if self.prison_position:
                await asyncio.sleep(1)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"🤖 أهلاً بك @{user.username} في الغرفة! اكتب من 1 إلى 10 لترقص معي 🕺")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return
            
        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)
        username_lower = user.username.lower()

        if username_lower == "qais29":
            return

        # فحص الوصول لخط النهاية تلقائياً أثناء اللعب
        if self.game_active and self.finish_position and username_lower not in self.prisoners:
            distance_to_finish = ((current_x - self.finish_position.x)**2 + (current_z - self.finish_position.z)**2)**0.5
            if distance_to_finish < 1.3:
                await self.highrise.chat(f"🎉 كفو! الفائز الأسطوري @{user.username} وصل لخط النهاية! 🏆")
                if self.vip_position:
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        # رصد الحركة في الضوء الأحمر
        if not self.game_active or self.light == "green":
            self.player_positions[user.id] = (current_x, current_z)
            return

        if self.light == "red":
            old_pos = self.player_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance_moved = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                if distance_moved > 0.2:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 تم رصد حركة المخالف @{user.username} في الضوء الأحمر!")
                    try:
                        await self.highrise.send_emote("emote-kick")
                        await self.highrise.send_emote("emote-pushed", user.id)
                    except:
                        pass
                    await asyncio.sleep(1.5)
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
            else:
                self.player_positions[user.id] = (current_x, current_z)

    async def game_loop(self):
        try:
            while self.game_active:
                self.light = "green"
                await self.highrise.chat(f"🟢 ضوء أخضر! تحركوا بحذر! 🏃‍♂️")
                await asyncio.sleep(3.0)
                
                if not self.game_active: break
                
                self.light = "red"
                await self.highrise.chat(f"🔴 ضوء أحمر! قف مكاااانك! 🛑")
                await asyncio.sleep(random.uniform(3.0, 5.0))
                
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        # تنظيف الرسالة وتحويلها لأحرف صغيرة لمنع أي تجاهل للأوامر
        msg_clean = message.strip().lower()
        username_lower = user.username.lower()

        # استجابة الرقصات للجميع
        if msg_clean in self.dance_moves:
            try:
                await self.highrise.send_emote(self.dance_moves[msg_clean])
            except Exception as e:
                print(f"Error dancing: {e}")
            return

        # التحكم الخاص بك حصراً
        if username_lower == "qais29":
            
            # أمر تحديد السجن (اكتب /setprison أو سجن)
            if msg_clean in ["/setprison", "سجن"]:
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        print(f"📍 تم حفظ موقع السجن سحابياً: {pos.x}, {pos.y}, {pos.z}")
                        await self.highrise.chat("🔒 تم تسجيل موقع السجن الحالي بنجاح!")
                        return
            
            # أمر تحديد خط البداية (اكتب /setspawn أو بداية)
            elif msg_clean in ["/setspawn", "بداية", "خط البداية"]:
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.spawn_position = pos
                        print(f"📍 تم حفظ موقع البداية سحابياً: {pos.x}, {pos.y}, {pos.z}")
                        await self.highrise.chat("🟩 تم تسجيل خط الانطلاق والبداية بنجاح!")
                        return

            # أمر تحديد خط النهاية (اكتب /setfinish أو نهاية)
            elif msg_clean in ["/setfinish", "نهاية", "خط النهاية"]:
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.finish_position = pos
                        print(f"📍 تم حفظ موقع النهاية سحابياً: {pos.x}, {pos.y}, {pos.z}")
                        await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان والوصول!")
                        return

            # أمر تحديد منصة الـ VIP (اكتب /setvip)
            elif msg_clean == "/setvip":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.vip_position = pos
                        await self.highrise.chat("💎 تم تسجيل وتأمين منصة الـ VIP!")
                        return

            elif msg_clean == "نسخ اللباس":
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.username.lower() == "qais29":
                            await self.highrise.set_outfit(u.outfit)
                            await self.highrise.chat("👕 تم نسخ لباس القائد!")
                            break
                except:
                    pass

            elif msg_clean == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 تم بدء اللعبة وتفعيل الرادار التلقائي للضوء الأحمر والأخضر!")

            elif msg_clean == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    if self.game_task:
                        self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة والعودة للوضع المستقر.")
                    
        else:
            # منع الآخرين من التلاعب بالأوامر
            protected = ["/setprison", "سجن", "/setspawn", "بداية", "/setfinish", "نهاية", "ابدأ اللعبة", "اوقف اللعبة"]
            if msg_clean in protected:
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه صلاحيات القائد qais29 فقط!")

# =======================================================
# ⚙️ نظام التشغيل السحابي لـ Render
# =======================================================
if __name__ == "__main__":
    from highrise.__main__ import main as hr_main
    room_id = "69fea9ea7ad83c6f1abffafe"
    api_token = "22b0110e1d415ec868f62fae55770b6b6c39edf1f02f8ec935e1741b2f61b2a5"
    
    sys.argv = ["highrise", "bot:MyBot", room_id, api_token]
    hr_main()
