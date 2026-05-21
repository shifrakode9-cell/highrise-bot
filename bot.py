import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الأساسية بنظام نقي ومحمي
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        
        self.player_positions = {}
        self.last_checked_positions = {}
        self.prisoners = set()
        self.game_task = None

        # 👮‍♂️ قائمة المشرفين (اكتب أسماء حساباتهم بالصغير هنا لتفعيل صلاحياتهم)
        self.moderators = ["qais29", "اسم_المشرف_الاول", "اسم_المشرف_الثاني"]

        # قاموس الـ 10 رقصات
        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop", "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 بوت لعبة Squid Game - النسخة الكاملة والمصلحة 100% جاهزة!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if isinstance(position, Position):
            self.player_positions[user.id] = position
            self.last_checked_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        username_lower = user.username.lower()

        # تموضع البوت التلقائي في المنتصف عند الدخول
        try:
            bot_info = await self.highrise.get_bot_info()
            if user.id == bot_info.user.id:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(bot_info.user.id, Position(17.0, 0.0, 17.0, "FrontRight"))
                return
        except Exception as e:
            print(f"Error auto-moving bot: {e}")

        # 👑 ترحيب بالقائد الأعلى قيس
        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الغرفة تحت تصرفك والعدالة جاهزة.")
            return

        # 🔒 إرجاع السجين الهارب فوراً عند الدخول
        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ عد إلى السجن يا @{user.username}! لا هروب من العدالة!")
            if self.prison_position:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        # 👋 ترحيب تلقائي بكافة اللاعبين الجدد
        await self.highrise.chat(f"✨ أهلاً بك @{user.username} في غرفتنا الأسطورية! استمتع معنا بلعبة الحبار! 🦑")

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

        # 1️⃣ فحص خط النهاية والممر بالكامل للفائزين تلقائياً
        if self.game_active and self.finish_position and username_lower not in self.prisoners:
            if current_z >= round(self.finish_position.z, 1) and abs(current_x - self.finish_position.x) < 7.5:
                await self.highrise.chat(f"🎉 مبروك للفائز الأسطوري @{user.username}! نقل مباشر وفوري إلى الـ VIP! 🏆")
                if self.vip_position:
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        # 2️⃣ حماية منطقة الـ VIP من المتسللين العاديين
        if self.vip_position and username_lower not in self.prisoners:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5:
                if self.finish_position and current_z >= round(self.finish_position.z, 1):
                    return
                self.prisoners.add(username_lower)
                await self.highrise.chat(f"🚨 تسلل مرفوض يا @{user.username}! خذ لكمة السقوط الدرامي إلى السجن! 🥊")
                try: await self.highrise.send_emote("emote-die", user.id)
                except: pass
                await asyncio.sleep(2.5) 
                if self.prison_position:
                    await self.highrise.teleport(user.id, self.prison_position)
                return

        # 3️⃣ الرصد الحازم في الضوء الأحمر 
        if self.game_active and self.light == "red" and username_lower not in self.prisoners:
            old_pos = self.last_checked_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance = ((current_x - old_x)**2 + (current_z - old_z)**2)**0.5
                if distance > 0.18:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 لُقطت! المخالف @{user.username} تحرك في الأحمر! إلى السجن! 🥊")
                    try: await self.highrise.send_emote("emote-die", user.id)
                    except: pass
                    await asyncio.sleep(2.5) 
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
                    return 
            
        self.last_checked_positions[user.id] = (current_x, current_z)

    # 💰 إيداع 5 جولد للحصالة: نقل مباشر لخط البداية بربط الهوية الصريحة
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if tip.type == "gold" and tip.amount >= 5:
            sender_lower = sender.username.lower()
            if sender_lower in self.prisoners:
                self.prisoners.remove(sender_lower)
                await self.highrise.chat(f"💰 كفالة مقبولة! رشة ماء وإفراج فوري عن @{sender.username} لخط البداية! 🌊🕊️")
                try: await self.highrise.send_emote("emote-wave", sender.id)
                except: pass
                if self.spawn_position:
                    await asyncio.sleep(1.0)
                    await self.highrise.teleport(sender.id, self.spawn_position)
            else:
                await self.highrise.chat(f"❤️ شكراً لك يا غالي @{sender.username} على دعمك الكريم بـ {tip.amount} جولد!")

    # 🔄 نظام الأضواء مع تثبيت وقت الأخضر لـ 2.5 ثانية والأحمر العشوائي
    async def game_loop(self):
        try:
            while self.game_active:
                for uid, pos in self.player_positions.items():
                    if isinstance(pos, Position):
                        self.last_checked_positions[uid] = (round(pos.x, 1), round(pos.z, 1))

                round_choice = random.choice(["green_round", "red_round", "repeat_red_round"])

                if round_choice == "green_round":
                    self.light = "green"
                    await self.highrise.chat("🟢 ضوء أخضر (ثانيتين ونصف كاملة)! اركضوا! 🏃‍♂️")
                    await asyncio.sleep(2.5)
                
                elif round_choice == "red_round":
                    self.light = "red"
                    await self.highrise.chat("🔴 ضوء أحمر!!! قف مكانك تماماً! 🛑")
                    await asyncio.sleep(random.uniform(2.5, 4.5))
                
                elif round_choice == "repeat_red_round":
                    self.light = "red"
                    await self.highrise.chat("🔴 ضوء أحمر!!! قف مكانك! 🛑")
                    await asyncio.sleep(random.uniform(2.0, 3.5))
                    if not self.game_active: break
                    await self.highrise.chat("🚨 تكرار الضوء الأحمر فجأة!!! ممنوع الحركة نهائياً! 🛑")
                    await asyncio.sleep(random.uniform(2.0, 3.5))

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        if message in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message], user.id)
            except: pass
            return

        # فحص الصلاحيات الفولاذي للقائد وللمشرفين
        if username_lower == "qais29" or username_lower in self.moderators:
            pos = self.player_positions.get(user.id)
            
            if message == "/setprison" and pos:
                self.prison_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🔒 تم تسجيل موقع السجن بنجاح!")
            
            elif message == "/setspawn" and pos:
                self.spawn_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")

            elif message == "/setvip" and pos:
                self.vip_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("💎 تم تحديد منصة الـ VIP وحمايتها الفولاذية!")

            elif message == "/setfinish" and pos:
                self.finish_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان والممر بالعرض الكامل بنجاح!")

            elif message == "/setbot":
                await self.highrise.chat("🤖 أنا مستقر في منتصف الممر ومستعد تماماً للحكم وإشعال الغرفة!")

            elif message == "نسخ اللباس" and username_lower == "qais29":
                try:
                    if user.outfit:
                        await self.highrise.set_outfit(user.outfit)
                        await self.highrise.chat("👕 تم نسخ لباسك بنجاح يا قائد!")
                except: pass

            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    if not self.spawn_position or not self.finish_position or not self.prison_position:
                        await self.highrise.chat("⚠️ يرجى تحديد المواقع أولاً: خط الانطلاق ونهاية الأمان والسجن!")
                        return
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 بدأت لعبة الحبار الأسطورية! جولات عشوائية ومفاجئة ومؤثرات حماسية بدأت الآن! 🛑")

            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة وإلغاء الرصد بنجاح.")

            # 💎 نظام الـ VIP المتطور للإدارة والمشرفين
            elif message.startswith("vip"):
                parts = message.split()
                
                # الحالة الأولى: نقل لاعب آخر بواسطة الإدارة (vip @player)
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    
                    for uid, upos in list(self.player_positions.items()):
                        try:
                            user_list = await self.highrise.get_room_users()
                            for room_user, pos_item in user_list.users:
                                if room_user.username.lower() == target_username:
                                    if target_username in self.prisoners:
                                        self.prisoners.remove(target_username)
                                    
                                    await self.highrise.chat(f"👑 بأمر من الإدارة، تم سحب @{room_user.username} إلى منصة الـ VIP! 💎")
                                    if self.vip_position:
                                        await self.highrise.teleport(room_user.id, self.vip_position)
                                        await self.highrise.send_emote("dance-praise", room_user.id)
                                    return
                        except: pass
                        
                # الحالة الثانية: عندما يكتب قيس أو المشرف كلمة vip لنفسه (السطر الذي كان مقطوعاً وتم إصلاحه هنا)
                else:
                    if username_lower in self.prisoners:
                        self.prisoners.remove(username_lower)
                    
                    await self.highrise.chat(f"👑 أهلاً بالقادة! تم نقلك فوراً يا @{user.username} إلى الـ VIP! 💎")
                    if self.vip_position:
                        try:
                            await self.highrise.teleport(user.id, self.vip_position)
                            await self.highrise.send_emote("dance-praise", user.id)
                        except: pass

            elif message.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم العفو عن @{target_username} ونقله لخط البداية بكامل طاقته! 🌊")
                        
                        for uid, upos in self.player_positions.items():
                            try:
                                await self.highrise.send_emote("emote-wave", uid)
                                if self.spawn_position:
                                    await self.highrise.teleport(uid, self.spawn_position)
                            except: pass
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في السجن أصلاً.")
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setbot", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة", "vip"]
            if message in protected_commands or message.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذا الأمر الحاسم مخصص للإدارة والمشرفين فقط!")
