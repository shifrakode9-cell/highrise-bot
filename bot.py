import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False       
        self.glass_game_active = False 
        self.light = "red"
        
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        self.door_position = None  
        
        self.glass_positions = {}  
        self.glass_traps = {}      
        
        self.player_positions = {}
        self.prisoners = set()  
        self.game_task = None
        self.freeze_check = False  
        
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
        print("🚀 Bot started successfully after full syntax validation!")

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
        
        if user.id in self.prisoners and self.prison_position:
            await asyncio.sleep(2.0)
            try: 
                await self.highrise.teleport(user.id, self.prison_position)
            except: 
                pass

    async def release_prisoner_via_gold(self, target_id: str):
        if target_id in self.prisoners:
            self.prisoners.remove(target_id)
            room_users = await self.highrise.get_room_users()
            display_name = "اللاعب"
            for u, _ in room_users.content:
                if u.id == target_id:
                    display_name = f"@{u.username}"
                    break
            await self.highrise.chat(f"🔓 تم تحرير {display_name} من السجن بفضل الدعم!")
            if self.spawn_position:
                try:
                    await self.highrise.teleport(target_id, self.spawn_position)
                    await asyncio.sleep(0.7)
                    await self.highrise.teleport(target_id, self.spawn_position)  
                except Exception as e:
                    print(f"Teleport error: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        try:
            if sender.id in self.prisoners:
                await self.release_prisoner_via_gold(sender.id)
        except Exception as e:
            print(f"Error in on_tip: {e}")

    async def on_room_tip(self, sender_id: str, tips: list[tuple[User, CurrencyItem]]) -> None:
        try:
            if sender_id in self.prisoners:
                await self.release_prisoner_via_gold(sender_id)
                return
            for user_obj, currency_item in tips:
                if user_obj.id in self.prisoners:
                    await self.release_prisoner_via_gold(user_obj.id)
                    break
        except Exception as e:
            print(f"Error in on_room_tip: {e}")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return
        current_x = round(pos.x, 2)
        current_z = round(pos.z, 2)

        if user.id in self.prisoners:
            old_pos = self.player_positions.get(user.id)
            if old_pos and len(old_pos) == 2:
                if abs(current_x - old_pos[0]) > 0.03 or abs(current_z - old_pos[1]) > 0.03:
                    await self.release_prisoner_via_gold(user.id)
                    return

        if not self.game_active and not self.glass_game_active:
            return
        if user.id == self.highrise.my_id:
            return
        if self.light == "green" or self.freeze_check:
            self.player_positions[user.id] = (current_x, current_z)
            return

        if self.game_active and not self.glass_game_active:
            if self.finish_position and self.spawn_position and user.id not in self.prisoners:
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
                    await self.highrise.chat(f"🎉 مبروك الفوز @{user.username}! تم نقلك إلى الـ VIP!")
                    if self.vip_position:
                        try: 
                            await self.highrise.teleport(user.id, self.vip_position)
                        except: 
                            pass
                    return

            if user.id not in self.prisoners:
                old_pos = self.player_positions.get(user.id)
                if old_pos and len(old_pos) == 2:
                    old_x, old_z = old_pos
                    horizontal_distance = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                    if horizontal_distance > 0.29:  
                        await self.send_to_prison_with_effects(user)
                    else:
                        self.player_positions[user.id] = (current_x, current_z)
                else:
                    self.player_positions[user.id] = (current_x, current_z)

        elif self.glass_game_active and not self.game_active:
            if user.id not in self.prisoners:
                on_safe_side = False
                for key, saved_pos in self.glass_positions.items():
                    if "_side" in key:
                        if abs(current_x - round(saved_pos.x, 2)) <= 0.35 and abs(current_z - round(saved_pos.z, 2)) <= 0.35:
                            on_safe_side = True
                            break
                if on_safe_side:
                    self.player_positions[user.id] = (current_x, current_z)
                    return

                for key, saved_pos in self.glass_positions.items():
                    if "_side" not in key:
                        if abs(current_x - round(saved_pos.x, 2)) <= 0.95 and abs(current_z - round(saved_pos.z, 2)) <= 0.95:
                            if self.glass_traps.get(key) == "trap":
                                await self.highrise.chat(f"💥 سقط @{user.username} في الزجاج الفخ إلى السجن!")
                                await self.send_to_prison_with_effects(user)
                                break

    async def send_to_prison_with_effects(self, user: User):
        self.prisoners.add(user.id)
        death_scenario = random.choice(["dead", "faint", "sad"])
        try:
            if death_scenario == "dead": 
                await self.highrise.send_emote("emote-dead", user.id)
            elif death_scenario == "faint": 
                await self.highrise.send_emote("dance-drop", user.id)
            else: 
                await self.highrise.send_emote("emote-sad", user.id)
        except: 
            pass
        await asyncio.sleep(2.5) 
        if self.prison_position:
            try: 
                await self.highrise.teleport(user.id, self.prison_position)
            except: 
                pass

    async def on_chat(self, user: User, message: str) -> None:
        message_clean = message.strip().lower()
        if message_clean in self.dance_moves:
            try: 
                await self.highrise.send_emote(self.dance_moves[message_clean], user.id)
            except: 
                pass
            return

        if await self.has_permissions(user):
            room_users = await self.highrise.get_room_users()

            if message_clean == "/setprison":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تحديد موقع السجن بنجاح!")
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
                        await self.highrise.chat("💎 تم تحديد منصة الـ VIP!")
                        break
            elif message_clean == "/setfinish":
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.finish_position = pos
                        await self.highrise.chat("🏁 تم تحديد خط النهاية بنجاح!")
                        break
            elif message_clean.startswith("/setglass"):
                parts = message_clean.split()
                if len(parts) == 3:
                    step = parts[1]     
                    direction = parts[2]  
                    tile_id = None
                    if direction in ["right", "r", "يمين"]: tile_id = "right"
                    elif direction in ["left", "l", "يسار"]: tile_id = "left"
                    elif direction in ["side", "s", "جانبي", "جانب"]: tile_id = "side"
                    if tile_id and step.isdigit():
                        for u, pos in room_users.content:
                            if u.id == user.id and isinstance(pos, Position):
                                key = f"{step}_{tile_id}"
                                self.glass_positions[key] = pos
                                await self.highrise.chat(f"💎 تم حفظ المربع {tile_id} في الصف {step}")
                                break

            elif message_clean == "ابدأ اللعبة":
                self.glass_game_active = False
                self.game_active = True
                self.prisoners.clear()
                self.player_positions.clear()
                self.freeze_check = False
                for u, pos in room_users.content:
                    if hasattr(pos, 'x'):
                        self.player_positions[u.id] = (round(pos.x, 2), round(pos.z, 2))
                if self.game_task and not self.game_task.done():
                    self.game_task.cancel()
                self.game_task = asyncio.create_task(self.game_loop())
                await self.highrise.chat("🎮 انطلقت لعبة أحمر وأخضر بنجاح!")

            elif message_clean in ["اوقف اللعبة", "اوقف الزجاج"]:
                self.game_active = False
                self.glass_game_active = False
                self.freeze_check = False
                if self.game_task:
                    self.game_task.cancel()
                    self.game_task = None
                self.prisoners.clear() 
                self.player_positions.clear()  
                await self.highrise.chat("🛑 تم إيقاف اللعب وإعادة الجميع للانطلاق.")
                if self.spawn_position:
                    for u, _ in room_users.content:
                        if u.id != self.highrise.my_id:
                            try: 
                                await self.highrise.teleport(u.id, self.spawn_position)
                            except: 
                                pass

            elif message_clean == "ابدأ الزجاج":
                self.game_active = False
                if self.game_task:
                    self.game_task.cancel()
                    self.game_task = None
                self.glass_game_active = True
                self.glass_traps.clear()
                self.prisoners.clear()
                self.player_positions.clear()
                for block in range(0, 10): 
                    is_right_trap = random.choice([True, False])
                    for sub in range(1, 4):
                        step_num = block * 3 + sub
                        self.glass_traps[f"{step_num}_side"] = "safe"
                        if is_right_trap:
                            self.glass_traps[f"{step_num}_right"] = "trap"
                            self.glass_traps[f"{step_num}_left"] = "safe"
                        else:
                            self.glass_traps[f"{step_num}_left"] = "trap"
                            self.glass_traps[f"{step_num}_right"] = "safe"
                await self.highrise.chat("⚡ تم تشغيل لعبة الجسر الزجاجي!")

            elif message_clean.startswith("vip"):
                parts = message.split()
                if len(parts) > 1 and self.vip_position:
                    target = await self.get_target_user(parts[1], room_users)
                    if target:
                        try: 
                            await self.highrise.teleport(target.id, self.vip_position)
                        except: 
                            pass

            elif message_clean.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target = await self.get_target_user(parts[1], room_users)
                    if target:
                        if target.id in self.prisoners:
                            self.prisoners.remove(target.id)
                            await self.highrise.chat(f"🕊️ تم الإفراج عن @{target.username}")
                            if self.spawn_position:
                                try:
                                    await self.highrise.teleport(target.id, self.spawn_position)
                                    await asyncio.sleep(1.0)
                                    await self.highrise.teleport(target.id, self.spawn_position)
                                except: 
                                    pass
                        else:
                            await self.highrise.chat(f"@{target.username} ليس مسجوناً.")
        else:
            protected = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setglass", "ابدأ اللعبة", "اوقف اللعبة", "ابدأ الزجاج", "اوقف الزجاج"]
            if message_clean in protected or message_clean.startswith("vip") or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username} الأمر للمشرفين فقط!")

    async def update_all_positions(self, room_users):
        for u, pos in room_users.content:
            if hasattr(pos, 'x'):
                self.player_positions[u.id] = (round(pos.x, 2), round(pos.z, 2))

    async def game_loop(self):
        try:
            while self.game_active:
                events = ["green_silent", "fake_signal", "red_silent"]
                random.shuffle(events)
                for current_event in events:
                    if not self.game_active: 
                        break
                    room_users = await self.highrise.get_room_users()
                    
                    if current_event == "green_silent":
                        self.light = "green"
                        await self.highrise.chat("🟢 ضوء أخضر! انطلقوا الآن!")
                        await asyncio.sleep(random.uniform(0.5, 1.9))
                        self.freeze_check = True
                        self.light = "red"
                        await self.update_all_positions(room_users)
                        await asyncio.sleep(0.4)
                        self.freeze_check = False
                        await asyncio.sleep(random.uniform(0.6, 1.8))

                    elif current_event == "fake_signal":
                        fake_msg = random.choice([
                            "🛑 قف مكانك... امزح معكم تحركوا!",
                            "🛑 استعدوا... الضوء أوشك أن يقلب!",
                            "🛑 هل أنتم جاهزون للتوقف؟"
                        ])
                        self.light = "green"
                        await self.highrise.chat(fake_msg)
                        await asyncio.sleep(random.uniform(0.7, 1.9))

                    elif current_event == "red_silent":
                        self.freeze_check = True
                        self.light = "red"
                        await self.update_all_positions(room_users)
                        await asyncio.sleep(0
