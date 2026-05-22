import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الأساسية
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        
        self.player_positions = {}
        self.last_checked_positions = {}
        self.prisoners = set()
        self.game_task = None

        # 👮‍♂️ اكتب أسماء حسابات المشرفين هنا بالأحرف الصغيرة تماماً لتفعيل صلاحياتهم
        self.moderators = ["qais29", "اسم_المشرف_الاول", "اسم_المشرف_الثاني"]

        # قاموس الـ 10 رقصات
        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop", "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 نسخة البوت الاحترافية - عشوائية تكرار الأحمر والأخضر المطور جاهزة!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if isinstance(position, Position):
            self.player_positions[user.id] = position
            self.last_checked_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        username_lower = user.username.lower()

        try:
            bot_info = await self.highrise.get_bot_info()
            if user.id == bot_info.user.id:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(bot_info.user.id, Position(17.0, 0.0, 17.0, "FrontRight"))
                return
        except Exception as e:
            print(f"Error moving bot: {e}")

        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الغرفة تحت تصرفك.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ عد إلى السجن يا @{user.username}!")
            if self.prison_position:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"✨ أهلاً بك @{user.username} في اللعبة!")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if isinstance(pos, Position):
            self.player_positions[user.id] = pos
        else:
            return

        username_lower = user.username.lower()
        if username_lower == "qais29":
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)

        # فحص هل اللاعب تجاوز خط النهاية ودخل منطقة الأمان؟
        is_in_safe_zone = False
        if self.finish_position and current_z >= round(self.finish_position.z, 1) and abs(current_x - self.finish_position.x) < 7.5:
            is_in_safe_zone = True

        # 1️⃣ رصد الحركة في الضوء الأحمر (يطبق فقط على من لم يصل لخط الأمان بعد)
        if self.game_active and self.light == "red" and username_lower not in self.prisoners and not is_in_safe_zone:
            old_pos = self.last_checked_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance = ((current_x - old_x)**2 + (current_z - old_z)**2)**0.5
                if distance > 0.18:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 حركة في الأحمر! المخالف @{user.username} إلى السجن فوراً! 🥊")
                    try: await self.highrise.send_emote("emote-die", user.id)
                    except: pass
                    await asyncio.sleep(2.0) 
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
                    return 

        # 2️⃣ فحص الفوز والـ VIP: لا يتحقق إلا إذا كان الضوء أخضر ودخل اللاعب منطقة الأمان فعلياً
        if self.game_active and self.light == "green" and is_in_safe_zone and username_lower not in self.prisoners:
            await self.highrise.chat(f"🎉 مبروك الفوز الأسطوري @{user.username}! نقل إلى الـ VIP! 🏆")
            if self.vip_position:
                await self.highrise.teleport(user.id, self.vip_position)
            return

        # 3️⃣ حماية منطقة الـ VIP من المتسللين يدوياً
        if self.vip_position and username_lower not in self.prisoners:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5 and not is_in_safe_zone:
                self.prisoners.add(username_lower)
                await self.highrise.chat(f"🚨 تسلل مرفوض يا @{user.username}! إلى السجن! 🥊")
                try: await self.highrise.send_emote("emote-die", user.id)
                except: pass
                await asyncio.sleep(2.0) 
                if self.prison_position:
                    await self.highrise.teleport(user.id, self.prison_position)
                return
            
        self.last_checked_positions[user.id] = (current_x, current_z)

    # 💰 دالة رصد الدفع في حصالة الغرفة (Room Tip Jar) لإخراج المسجونين لخط البداية
    async def on_room_tip(self, sender: User, tips: list[CurrencyItem]) -> None:
        for tip in tips:
            if tip.type == "gold" and tip.amount >= 5:
                sender_lower = sender.username.lower()
                if sender_lower in self.prisoners:
                    self.prisoners.remove(sender_lower)
                    await self.highrise.chat(f"💰 كفالة مقبولة في حصالة الغرفة! إفراج فوري عن @{sender.username} إلى خط البداية! 🕊️")
                    if self.spawn_position:
                        await asyncio.sleep(0.5)
                        await self.highrise.teleport(sender.id, self.spawn_position)
                else:
                    await self.highrise.chat(f"❤️ شكراً لك @{sender.username} على دعم الغرفة وحصالتها بـ {tip.amount} جولد!")

    # 🔄 نظام الأضواء المطور: تكرار عشوائي للأحمر (1 أو 2 أو 3 مرات) وتكرار محكوم للأخضر
    async def game_loop(self):
        try:
            while self.game_active:
                for uid, pos in self.player_positions.items():
                    if isinstance(pos, Position):
                        self.last_checked_positions[uid] = (round(pos.x, 1), round(pos.z, 1))

                # بناء دورة أضواء عشوائية مباغتة تماماً
                # نختار كم مرة سيتكرر الأحمر في هذه الدورة (من 1 إلى 3 مرات عشوائياً)
                red_repeats = random.randint(1, 3)
                
                # نختار هل الأخضر سيظهر مرة واحدة أم سيتكرر مرتين في هذه الدورة
                green_repeats = random.choice([1, 2])
                
                # دمج العناصر في قائمة واحدة لخلطها عشوائياً
                pool = ["green"] * green_repeats + ["red"] * red_repeats
                random.shuffle(pool)

                for light_type in pool:
                    if not self.game_active: break

                    if light_type == "green":
                        self.light = "green"
                        await self.highrise.chat("🟢 ضوء أخضر! اركضوا! 🏃‍♂️")
                        await asyncio.sleep(2.3) # التزام تام بوقت 2.3 ثانية
                    
                    elif light_type == "red":
                        self.light = "red"
                        # تنويع عبارات الأحمر لإضافة حماس مباغت للاعبين بناءً على التكرار
                        alert_msg = random.choice([
                            "🔴 ضوء أحمر!!! قف مكانك تماماً! 🛑",
                            "🚨 تكرار الضوء الأحمر فجأة!!! ممنوع الحركة! 🛑",
                            "🛑 تثبيت!!! ضوء أحمر مباغت، لا تتحرك! 🔴"
                        ])
                        await self.highrise.chat(alert_msg)
                        await asyncio.sleep(random.uniform(2.3, 4.3))

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        message_clean = message.strip().lower()
        username_lower = user.username.lower()

        if message_clean in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message_clean], user.id)
            except: pass
            return

        # 👑 التحقق المشترك والفوري من صلاحيات الإدارة (قيس والمشرفين)
        if username_lower == "qais29" or username_lower in self.moderators:
            pos = self.player_positions.get(user.id)
            
            if message_clean == "/setprison" and pos:
                self.prison_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🔒 تم تسجيل موقع السجن بنجاح!")
            
            elif message_clean == "/setspawn" and pos:
                self.spawn_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")

            elif message_clean == "/setvip" and pos:
                self.vip_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("💎 تم تحديد منصة الـ VIP بنجاح!")

            elif message_clean == "/setfinish" and pos:
                self.finish_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🏁 تم تسجيل خط النهاية بنجاح!")

            elif message_clean == "/setbot":
                await self.highrise.chat("🤖 البوت مستعد تماماً للحكم!")

            elif message_clean == "نسخ اللباس" and username_lower == "qais29":
                try:
                    if user.outfit:
                        await self.highrise.set_outfit(user.outfit)
                        await self.highrise.chat("👕 تم نسخ لباسك بنجاح يا قائد!")
                except: pass

            elif message_clean == "ابدأ اللعبة":
                if not self.game_active:
                    if not self.spawn_position or not self.finish_position or not self.prison_position:
                        await self.highrise.chat("⚠️ يرجى تحديد المواقع أولاً!")
                        return
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 بدأت اللعبة بنظام الأضواء المباغت والمطور! 🛑")

            elif message_clean == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة بنجاح.")

            # 💎 نظام نقل الـ VIP السريع والمضمون كلياً عبر الذاكرة الداخلية للبوت
            elif message_clean.startswith("vip"):
                parts = message.split()
                
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    
                    player_found = False
                    try:
                        room_users = await self.highrise.get_room_users()
                        for room_user, pos_item in room_users.users:
                            if room_user.username.lower() == target_username:
                                if target_username in self.prisoners:
                                    self.prisoners.remove(target_username)
                                
                                await self.highrise.chat(f"👑 تم نقل @{room_user.username} إلى الـ VIP بأمر من الإدارة! 💎")
                                if self.vip_position:
                                    await self.highrise.teleport(room_user.id, self.vip_position)
                                player_found = True
                                return
                        if not player_found:
                            await self.highrise.chat("⚠️ هذا اللاعب غير متواجد في الغرفة حالياً.")
                    except: pass
                        
                else:
                    if username_lower in self.prisoners:
                        self.prisoners.remove(username_lower)
                    
                    await self.highrise.chat(f"👑 تم نقلك فوراً يا @{user.username} إلى الـ VIP! 💎")
                    if self.vip_position:
                        try: await self.highrise.teleport(user.id, self.vip_position)
                        except: pass

            elif message_clean.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم الإفراج عن @{target_username}! 🌊")
                        
                        try:
                            room_users = await self.highrise.get_room_users()
                            for room_user, pos_item in room_users.users:
                                if room_user.username.lower() == target_username:
                                    if self.spawn_position:
                                        await self.highrise.teleport(room_user.id, self.spawn_position)
                                    return
                        except: pass
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في السجن.")
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setbot", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة", "vip"]
            if message_clean in protected_commands or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذا الأمر مخصص للإدارة والمشرفين!")
