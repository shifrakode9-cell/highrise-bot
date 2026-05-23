import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        # إعدادات حالة الألعاب لضمان عدم التداخل والتجميد
        self.game_active = False       
        self.glass_game_active = False 
        self.light = "red"
        
        # إحداثيات المواقع الأساسية للغرفة
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        self.door_position = None  
        
        # إحداثيات الجسر الزجاجي
        self.glass_positions = {}  
        self.glass_traps = {}      
        
        # حفظ سجلات المواقع واللاعبين
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None
        
        # قائمة الـ 20 رقصة العامة للغرفة
        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop",
            "10": "dance-handsup", "11": "dance-flex", "12": "emote-shy",
            "13": "dance-vogue", "14": "emote-sad", "15": "dance-orangejust",
            "16": "emote-laughing", "17": "dance-tiktok2", "18": "emote-celebrate",
            "19": "dance-macarena", "20": "emote-charging"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 تم تحديث الكود: الحساسية الفائقة وتفخخ المجموعات الثلاثية جاهزة!")

    async def has_permissions(self, user: User) -> bool:
        username_lower = user.username.lower()
        if username_lower in ["qais29", "sweet_lulus"]:
            return True
        try:
            permissions = await self.highrise.get_room_privileges(user.id)
            if permissions.content.moderator or permissions.content.designer:
                return True
        except Exception as e:
            print(f"Error checking privileges: {e}")
        return False

    async def get_target_user(self, target_name: str, room_users):
        clean_name = target_name.replace("@", "").strip().lower()
        for u, _ in room_users.content:
            if u.username.lower() == clean_name:
                return u
        return None

    async def on_user_join(self, user: User, position: Position) -> None:
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
            if self.door_position is None:
                self.door_position = position
        
        username_lower = user.username.lower()
        if username_lower in self.prisoners and self.prison_position:
            await asyncio.sleep(2.0)
            try: await self.highrise.teleport(user.id, self.prison_position)
            except: pass

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)
        username_lower = user.username.lower()

        if user.id == self.highrise.my_id:
            return

        # ---------------- اللعبة الأولى: أحمر وأخضر (حساسية فائقة) ----------------
        if self.game_active and not self.glass_game_active:
            if self.finish_position and self.spawn_position and username_lower not in self.prisoners:
                is_winner = False
                if abs(self.finish_position.x - self.spawn_position.x) > abs(self.finish_position.z - self.spawn_position.z):
                    if (self.finish_position.x >= self.spawn_position.x and current_x >= self.finish_position.x - 0.5) or \
                       (self.finish_position.x < self.spawn_position.x and current_x <= self.finish_position.x + 0.5):
                        is_winner = True
                else:
                    if (self.finish_position.z >= self.spawn_position.z and current_z >= self.finish_position.z - 0.5) or \
                       (self.finish_position.z < self.spawn_position.z and current_z <= self.finish_position.z + 0.5):
                        is_winner = True

                if is_winner:
                    await self.highrise.chat(f"🎉 مبروك للفائز الأسطوري @{user.username}! لقد وصل لخط الأمان وتم نقله للـ VIP! 🏆")
                    if self.vip_position:
                        try: await self.highrise.teleport(user.id, self.vip_position)
                        except: pass
                    return

            if self.light == "green":
                self.player_positions[user.id] = (current_x, current_z)
                return

            if self.light == "red" and username_lower not in self.prisoners:
                old_pos = self.player_positions.get(user.id)
                if old_pos:
                    old_x, old_z = old_pos
                    distance = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                    # الحساسية العالية جداً تم تعديلها هنا إلى 0.08 لرصد أقل اهتزاز
                    if distance > 0.08:  
                        await self.send_to_prison_with_effects(user)
                else:
                    self.player_positions[user.id] = (current_x, current_z)

        # ---------------- اللعبة الثانية: الجسر الزجاجي المكسور (نظام المجموعات) ----------------
        elif self.glass_game_active and not self.game_active:
            if username_lower not in self.prisoners:
                for key, saved_pos in self.glass_positions.items():
                    if abs(current_x - round(saved_pos.x, 1)) <= 0.2 and abs(current_z - round(saved_pos.z, 1)) <= 0.2:
                        if self.glass_traps.get(key) == "trap":
                            await self.highrise.chat(f"💥 كسر الزجاج المكسور! وسقط @{user.username} مباشرة إلى السجن! 💀")
                            await self.send_to_prison_with_effects(user)
                        break

    async def send_to_prison_with_effects(self, user: User):
        username_lower = user.username.lower()
        self.prisoners.add(username_lower)
        
        death_scenario = random.choice(["dead", "faint", "sad"])
        try:
            if death_scenario == "dead": await self.highrise.send_emote("emote-dead", user.id)
            elif death_scenario == "faint": await self.highrise.send_emote("dance-drop", user.id)
            else: await self.highrise.send_emote("emote-sad", user.id)
        except: pass
        
        await asyncio.sleep(2.5) 
        if self.prison_position:
            try: await self.highrise.teleport(user.id, self.prison_position)
            except: pass

    async def game_loop(self):
        try:
            while self.game_active:
                events = ["green", "red_fake", "red_normal"]
                random.shuffle(events)
                for current_event in events:
                    if not self.game_active: break
                    
                    if current_event == "green":
                        self.light = "green"
                        await self.highrise.chat("🟢 ضوء أخضر! تحركوا بحذر! [المدة: 2.0 ثانية] 🏃‍♂️")
                        await asyncio.sleep(2.0) 
                    elif current_event == "red_fake":
                        self.light = "red"
                        await self.highrise.chat("🛑 خدعة! الضوء ما زال أحمر! قف مكانك ولا تتحرك! 🔴")
                        await asyncio.sleep(random.uniform(2.0, 3.5))
                    elif current_event == "red_normal":
                        self.light = "red"
                        await self.highrise.chat("🔴 ضوء أحمر! قف مكاااانك! 🛑")
                        await asyncio.sleep(random.uniform(3.0, 4.5))
        except asyncio.CancelledError:
            pass
        finally:
            self.light = "red"

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        sender_lower = sender.username.lower()
        receiver_lower = receiver.username.lower()
        if sender_lower in self.prisoners and receiver_lower == "qais29" and tip.amount >= 5:
            self.prisoners.remove(sender_lower)
            await self.highrise.chat(f"💰 كفالة معتمدة ({tip.amount}g)! حرية لـ @{sender.username} والعودة لخط البداية.")
            if self.spawn_position:
                try: await self.highrise.teleport(sender.id, self.spawn_position)
                except: pass

    async def on_chat(self, user: User, message: str) -> None:
        message_clean = message.strip().lower()
        
        if message_clean in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message_clean], user.id)
            except: pass
            return

        if await self.has_permissions(user):
            room_users = await self.highrise.get_room_users()

            if message_clean == "/setprison":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تحديد إحداثيات السجن بنجاح للعبتين!")
                        break
            
            elif message_clean == "/setspawn":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.spawn_position = pos
                        await self.highrise.chat("🟩 تم تحديد خط الانطلاق بنجاح!")
                        break

            elif message_clean == "/setvip":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.vip_position = pos
                        await self.highrise.chat("💎 تم تحديد منصة الـ VIP وحمايتها!")
                        break

            elif message_clean == "/setfinish":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.finish_position = pos
                        await self.highrise.chat("🏁 تم تحديد خط الأمان النهائي!")
                        break

            elif message_clean.startswith("/setglass"):
                parts = message_clean.split()
                if len(parts) == 3:
                    step = parts[1]     
                    side = parts[2]     
                    if side in ["right", "left"]:
                        for u, pos in room_users.content:
                            if u.id == user.id and isinstance(pos, Position):
                                key = f"{step}_{side}"
                                self.glass_positions[key] = pos
                                await self.highrise.chat(f"💎 تم حفظ الخطوة {step} الجانب {side} بنجاح!")
                                break

            elif message_clean == "ابدأ اللعبة":
                if not self.game_active and not self.glass_game_active:
                    self.game_active = True
                    self.player_positions.clear() 
                    for u, pos in room_users.content:
                        if hasattr(pos, 'x'):
                            self.player_positions[u.id] = (round(pos.x, 1), round(pos.z, 1))
                    
                    if self.game_task and not self.game_task.done():
                        self.game_task.cancel()
                    
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 انطلقت لعبة [أحمر وأخضر] بالحساسية الفائقة! 😈")

            elif message_clean == "اوقف اللعبة":
                self.game_active = False
                if self.game_task:
                    self.game_task.cancel()
                    self.game_task = None
                self.prisoners.clear() 
                self.player_positions.clear()  # تنظيف كامل للذاكرة لمنع التجمد مجدداً
                await self.highrise.chat("🛑 تم إيقاف لعبة [أحمر وأخضر] وإعادة تهيئة نظام الأوامر بنجاح.")
                if self.spawn_position:
                    for u, _ in room_users.content:
                        if u.id != self.highrise.my_id:
                            try: await self.highrise.teleport(u.id, self.spawn_position)
                            except: pass

            elif message_clean == "ابدأ الزجاج":
                if not self.glass_game_active and not self.game_active:
                    self.glass_game_active = True
                    self.glass_traps.clear()
                    
                    # هندسة تفخيخ المجموعات الثلاثية عشوائياً حتى مربع 24
                    groups = [
                        [1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12],
                        [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24]
                    ]
                    
                    for group in groups:
                        # اختيار عشوائي للجهة الكاملة المفخخة في المجموعة
                        if random.choice([True, False]):
                            for step in group:
                                self.glass_traps[f"{step}_right"] = "trap"
                                self.glass_traps[f"{step}_left"] = "safe"
                        else:
                            for step in group:
                                self.glass_traps[f"{step}_right"] = "safe"
                                self.glass_traps[f"{step}_left"] = "trap"
                            
                    await self.highrise.chat("⚡ تم تشغيل [الجسر الزجاجي] بنظام فخاخ المجموعات الثلاثية العشوائية! 🫨")

            elif message_clean == "اوقف الزجاج":
                # تنظيف كامل لجميع متغيرات لعبة الزجاج لاستقبال الأوامر مجدداً بدون قفل
                self.glass_game_active = False
                self.glass_traps.clear()
                self.prisoners.clear()
                self.player_positions.clear()
                await self.highrise.chat("🛑 تم إيقاف لعبة [الجسر الزجاجي] وإعادة تهيئة الذاكرة بنجاح.")
                if self.spawn_position:
                    for u, _ in room_users.content:
                        if u.id != self.highrise.my_id:
                            try: await self.highrise.teleport(u.id, self.spawn_position)
                            except: pass

            elif message_clean.startswith("vip"):
                parts = message.split()
                if len(parts) > 1 and self.vip_position:
                    target = await self.get_target_user(parts[1], room_users)
                    if target:
                        try: await self.highrise.teleport(target.id, self.vip_position)
                        except: pass
                        await self.highrise.chat(f"👑 بأمر الإدارة، تم نقل @{target.username} لمنصة الـ VIP.")

            elif message_clean.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target = await self.get_target_user(parts[1], room_users)
                    if target:
                        t_name_lower = target.username.lower()
                        if t_name_lower in self.prisoners:
                            self.prisoners.remove(t_name_lower)
                            await self.highrise.chat(f"🕊️ عفو إداري! تم الإفراج عن @{target.username} وإعادته لخط البداية.")
                            if self.spawn_position:
                                try: await self.highrise.teleport(target.id, self.spawn_position)
                                except: pass
                        else:
                            await self.highrise.chat(f"اللاعب @{target.username} ليس مسجوناً حالياً.")
                        
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setglass", "ابدأ اللعبة", "اوقف اللعبة", "ابدأ الزجاج", "اوقف الزجاج"]
            if message_clean in protected_commands or message_clean.startswith("vip") or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الأوامر حصرية للمشرفين المعتمدين!")
