import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الأساسية للغرفة
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        self.door_position = None  
        
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
        print("🤖 تم إصلاح دالة الحصالة نهائياً والبوت جاهز للعمل المستقر!")

    async def has_permissions(self, user: User) -> bool:
        """التحقق من الرتب المسموح لها بالتحكم باللعبة والإعدادات"""
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
        """البحث والتحقق الدقيق من اسم المستخدم المستهدف"""
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
            await self.highrise.teleport(user.id, self.prison_position)

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)
        username_lower = user.username.lower()

        if username_lower == "qais29" or user.id == self.highrise.my_id:
            return

        # 1️⃣ تدقيق ورصد خط النهاية والأمان للزوار الأحرار
        if self.game_active and self.finish_position and self.spawn_position and username_lower not in self.prisoners:
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
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        if not self.game_active or self.light == "green":
            self.player_positions[user.id] = (current_x, current_z)
            return

        # 2️⃣ تتبع ورصد الحركة أثناء الضوء الأحمر
        if self.light == "red" and username_lower not in self.prisoners:
            old_pos = self.player_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                
                if distance > 0.15:  
                    self.prisoners.add(username_lower)
                    
                    death_scenario = random.choice(["dead", "faint", "sad"])
                    if death_scenario == "dead":
                        await self.highrise.chat(f"⚠️ صيد ثمين! @{user.username} تحرك في الأحمر.. القضاء التام! 💀")
                        try: await self.highrise.send_emote("emote-dead", user.id)
                        except: pass
                    elif death_scenario == "faint":
                        await self.highrise.chat(f"⚠️ رصد حركة! @{user.username} يسقط مغشياً عليه من الصدمة! 🫨")
                        try: await self.highrise.send_emote("dance-drop", user.id)
                        except: pass
                    else: 
                        await self.highrise.chat(f"⚠️ كشف المحاولة! @{user.username} يتحسر على خسارته.. إلى السجن! 😭")
                        try: await self.highrise.send_emote("emote-sad", user.id)
                        except: pass
                    
                    await asyncio.sleep(3.5) 
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
            else:
                self.player_positions[user.id] = (current_x, current_z)

    async def game_loop(self):
        """حلقة إدارة جولات اللعبة بنظام الإشارات التلقائي العشوائي"""
        try:
            while self.game_active:
                events = ["green", "red_fake", "red_normal"]
                random.shuffle(events)
                
                for current_event in events:
                    if not self.game_active: 
                        break
                    
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

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        """تحرير تلقائي مصلح ومضمون 100% للمساجين عند دفع الكفالة للبوت مباشرة"""
        # تم إصلاح الشرط هنا ليعتمد على معرف البوت الرقمي بشكل دقيق وقاطع
        if receiver.id == self.highrise.my_id: 
            if sender.username.lower() in self.prisoners and tip.amount >= 5:
                self.prisoners.remove(sender.username.lower())
                await self.highrise.chat(f"💰 تم دفع الكفالة ({tip.amount}g) بنجاح! حرية لـ @{sender.username} والعودة لخط الانطلاق.")
                if self.spawn_position:
                    await self.highrise.teleport(sender.id, self.spawn_position)

    async def on_chat(self, user: User, message: str) -> None:
        message_clean = message.strip().lower()
        
        if message_clean in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message_clean], user.id)
            except Exception as e: print(f"Error executing dance: {e}")
            return

        if await self.has_permissions(user):
            room_users = await self.highrise.get_room_users()

            if message_clean == "/setprison":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تحديد إحداثيات السجن بنجاح!")
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
                        await self.highrise.chat("🏁 تم تحديد خط الأمان النهائي بكامل العرض!")
                        break

            elif message_clean == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    self.light = "red" 
                    self.player_positions.clear() 
                    for u, pos in room_users.content:
                        if hasattr(pos, 'x'):
                            self.player_positions[u.id] = (round(pos.x, 1), round(pos.z, 1))
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 انطلقت اللعبة بالتوقيتات المتوازنة والعشوائية المثالية! 😈")

            elif message_clean == "اوقف اللعبة":
                self.game_active = False
                self.light = "red"
                if self.game_task:
                    self.game_task.cancel()
                self.prisoners.clear() 
                await self.highrise.chat("🛑 تم إيقاف اللعبة. إعادة اللاعبين لخط البداية، وعودة البوت التلقائية للباب الرئيسي!")
                
                if self.spawn_position:
                    for u, _ in room_users.content:
                        if u.id != self.highrise.my_id:
                            await self.highrise.teleport(u.id, self.spawn_position)
                
                if self.door_position:
                    await self.highrise.teleport(self.highrise.my_id, self.door_position)

            elif message_clean.startswith("vip"):
                parts = message.split()
                if len(parts) > 1 and self.vip_position:
                    target = await self.get_target_user(parts[1], room_users)
                    if target:
                        await self.highrise.teleport(target.id, self.vip_position)
                        await self.highrise.chat(f"👑 بأمر الإدارة، تم سحب الضيف @{target.username} لمنصة الـ VIP.")
                    else:
                        await self.highrise.chat("❌ لم أتمكن من العثور على هذا اللاعب بالغرفة بدقة.")

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
                                await self.highrise.teleport(target.id, self.spawn_position)
                        else:
                            await self.highrise.chat(f"اللاعب @{target.username} ليس مسجوناً حالياً.")
                    else:
                        await self.highrise.chat("❌ الاسم غير دقيق أو اللاعب غير موجود.")
                        
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "ابدأ اللعبة", "اوقف اللعبة"]
            if message_clean in protected_commands or message_clean.startswith("vip") or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الأوامر والامتيازات حصرية للمشرفين المعتمدين!")
