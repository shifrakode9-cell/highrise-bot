import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        # حالات الألعاب المعتمدة لمنع التعليق
        self.game_active = False       
        self.glass_game_active = False 
        self.light = "red"
        
        # إحداثيات المواقع الأساسية
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        self.door_position = None  
        
        # إحداثيات وفخاخ الجسر الزجاجي
        self.glass_positions = {}  
        self.glass_traps = {}      
        
        # السجلات والمؤقتات
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None
        
        # قائمة الـ 20 رقصة العامة
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
        print("🤖 تم تشغيل البوت وتحديث نظام إشعارات الحصالة المضمون!")

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
            self.player_positions[user.id] = (round(position.x, 2), round(position.z, 2))
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

        if not self.game_active and not self.glass_game_active:
            return

        if user.id == self.highrise.my_id:
            return

        current_x = round(pos.x, 2)
        current_z = round(pos.z, 2)
        username_lower = user.username.lower()

        # ---------------- اللعبة الأولى: أحمر وأخضر ----------------
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
                    if distance > 0.08:
                        await self.send_to_prison_with_effects(user)
                else:
                    self.player_positions[user.id] = (current_x, current_z)

        # ---------------- اللعبة الثانية: الجسر الزجاجي (الجهات المتقابلة) ----------------
        elif self.glass_game_active and not self.game_active:
            if username_lower not in self.prisoners:
                for key, saved_pos in self.glass_positions.items():
                    if abs(current_x - round(saved_pos.x, 2)) <= 0.2 and abs(current_z - round(saved_pos.z, 2)) <= 0.2:
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
                events = ["green_silent", "fake_signal", "red_silent"]
                random.shuffle(events)
                
                for current_event in events:
                    if not self.game_active: break
                    
                    if current_event == "green_silent":
                        self.light = "green"
                        await self.highrise.chat("🟢 ضوء أخضر! انطلقوا... [احسب وقتك بصمت!]")
                        green_duration = random.uniform(0.5, 1.9)
                        await asyncio.sleep(green_duration)
                        self.light = "red"
                        await asyncio.sleep(random.uniform(0.6, 1.8))

                    elif current_event == "fake_signal":
                        fake_msg = random.choice([
                            "🛑 قف مكانك... امزح معكم تحركوا!",
                            "🛑 استعدوا... الضوء أوشك أن يقلب!",
                            "⚠️ انتبهوا! الحساسية الآن تتضاعف!",
                            "🛑 هل أنتم جاهزون للتوقف؟"
                        ])
                        self.light = random.choice(["red", "green"])
                        await self.highrise.chat(fake_msg)
                        await asyncio.sleep(random.uniform(0.7, 1.9))

                    elif current_event == "red_silent":
                        self.light = "red"
                        red_duration = random.uniform(0.5, 1.9)
                        await asyncio.sleep(red_duration)
                        
        except asyncio.CancelledError:
            pass
        finally:
            self.light = "red"

    # 🛠️ نظام كشف وإشعار تفاعلي ومضمون 100% للحصالة داخل الغرفة
    async def on_room_tip(self, sender: User, tips: list[tuple[User, CurrencyItem]]) -> None:
        try:
            for receiver, item in tips:
                if receiver.username.lower() == "qais29":
                    # إرسال إشعار فوري في الشات يوضح أن هناك دعم وصلك بالفعل في الحصالة
                    await self.highrise.chat(f"📢 إشعار: استلم @{receiver.username} دعماً بقيمة {item.amount}g من @{sender.username} في الحصالة!")
                    
                    if item.amount >= 5:
                        sender_lower = sender.username.lower()
                        if sender_lower in self.prisoners:
                            self.prisoners.remove(sender_lower)
                            await self.highrise.chat(f"🔓 تم تأكيد كفالة الـ 5g بنجاح! إفراج عن @{sender.username} وعودته للانطلاق.")
                            if self.spawn_position:
                                try: await self.highrise.teleport(sender.id, self.spawn_position)
                                except: pass
                    break
        except Exception as e:
            print(f"Error handling room tip: {e}")

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
                    tile_id = parts[2]  
                    if tile_id in ["r1", "r2", "r3", "l1", "l2", "l3"]:
                        for u, pos in room_users.content:
                            if u.id == user.id and isinstance(pos, Position):
                                key = f"{step}_{tile_id}"
                                self.glass_positions[key] = pos
                                await self.highrise.chat(f"💎 تم حفظ الصف {step} المربع {tile_id} بنجاح!")
                                break

            elif message_clean == "ابدأ اللعبة":
                self.glass_game_active = False
                self.game_active = True
                self.prisoners.clear()
                self.player_positions.clear()
                
                for u, pos in room_users.content:
                    if hasattr(pos, 'x'):
                        self.player_positions[u.id] = (round(pos.x, 2), round(pos.z, 2))
                
                if self.game_task and not self.game_task.done():
                    self.game_task.cancel()
                
                self.game_task = asyncio.create_task(self.game_loop())
                await self.highrise.chat("🎮 انطلقت لعبة [أحمر وأخضر] بنظام التحدي الصامت والتمويه العشوائي! 🔥")

            elif message_clean == "اوقف اللعبة":
                self.game_active = False
                if self.game_task:
                    self.game_task.cancel()
                    self.game_task = None
                self.prisoners.clear() 
                self.player_positions.clear()  
                await self.highrise.chat("🛑 تم إيقاف لعبة [أحمر وأخضر] وتصفير السجلات تماماً.")
                if self.spawn_position:
                    for u, _ in room_users.content:
                        if u.id != self.highrise.my_id:
                            try: await self.highrise.teleport(u.id, self.spawn_position)
                            except: pass

            elif message_clean == "ابدأ الزجاج":
                self.game_active = False
                if self.game_task:
                    self.game_task.cancel()
                    self.game_task = None
                
                self.glass_game_active = True
                self.glass_traps.clear()
                self.prisoners.clear()
                self.player_positions.clear()
                
                for step in range(1, 25):
                    if random.choice([True, False]):
                        self.glass_traps[f"{step}_r1"] = "trap"
                        self.glass_traps[f"{step}_r2"] = "trap"
                        self.glass_traps[f"{step}_r3"] = "trap"
                        self.glass_traps[f"{step}_l1"] = "safe"
                        self.glass_traps[f"{step}_l2"] = "safe"
                        self.glass_traps[f"{step}_l3"] = "safe"
                    else:
                        self.glass_traps[f"{step}_l1"] = "trap"
                        self.glass_traps[f"{step}_l2"] = "trap"
                        self.glass_traps[f"{step}_l3"] = "trap"
                        self.glass_traps[f"{step}_r1"] = "safe"
                        self.glass_traps[f"{step}_r2"] = "safe"
                        self.glass_traps[f"{step}_r3"] = "safe"
                        
                await self.highrise.chat("⚡ تم تشغيل [الجسر الزجاجي] بنظام الجهات المتقابلة العشوائية بالكامل! 🫨")

            elif message_clean == "اوقف الزجاج":
                self.glass_game_active = False
                self.glass_traps.clear()
                self.prisoners.clear()
                self.player_positions.clear()
                await self.highrise.chat("🛑 تم إيقاف لعبة [الجسر الزجاجي] وتصفير السجلات تماماً.")
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
