import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الثابتة
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        
        # قواميس التتبع وتخزين بيانات المستخدمين
        self.player_positions = {}
        self.last_checked_positions = {}
        self.prisoners = set()
        self.game_task = None
        
        # متغير لضمان تكرار الأخضر متتالياً "مرة واحدة فقط" طوال جولة اللعبة
        self.double_green_triggered = False

        # 👮‍♂️ اكتب أسماء المشرفين هنا (بالأحرف الصغيرة)
        self.moderators = ["qais29", "اسم_المشرف_الاول", "اسم_المشرف_الثاني"]

        # قائمة الرقصات بالأرقام
        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop", "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 تم تفعيل محرك العشوائية المطلقة 100% - مستعد للعمل!")

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
        except: pass

        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! نظام التحكم بانتظارك.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ لا تحاول الهرب! عد إلى مكانك يا @{user.username}!")
            if self.prison_position:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"✨ أهلاً بك @{user.username} في الغرفة!")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not isinstance(pos, Position):
            return
        
        self.player_positions[user.id] = pos
        username_lower = user.username.lower()
        
        if username_lower == "qais29":
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)

        is_inside_safe_zone = False
        if self.finish_position and current_z >= round(self.finish_position.z, 1) and abs(current_x - self.finish_position.x) < 7.5:
            is_inside_safe_zone = True

        # 🚨 نظام السجن السينمائي الصارم في اللون الأحمر
        if self.game_active and self.light == "red" and username_lower not in self.prisoners and not is_inside_safe_zone:
            old_pos = self.last_checked_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance = ((current_x - old_x)**2 + (current_z - old_z)**2)**0.5
                if distance > 0.18:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 رصد حركي! @{user.username} تحرك في الأحمر! 🥊")
                    
                    try: await self.highrise.send_emote("emote-die", user.id)
                    except: pass
                    await asyncio.sleep(2.0)
                    
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
                        self.last_checked_positions[user.id] = (round(self.prison_position.x, 1), round(self.prison_position.z, 1))
                    return

        # 🟢 نظام الفوز الشرعي في اللون الأخضر (منطقة الأمان حصن للاعب)
        if self.game_active and self.light == "green" and is_inside_safe_zone and username_lower not in self.prisoners:
            await self.highrise.chat(f"🎉 فوز مستحق @{user.username}! تجاوزت خط الأمان ونقل للـ VIP! 🏆")
            if self.vip_position:
                await self.highrise.teleport(user.id, self.vip_position)
                self.last_checked_positions[user.id] = (round(self.vip_position.x, 1), round(self.vip_position.z, 1))
            return

        self.last_checked_positions[user.id] = (current_x, current_z)

    # 💰 نظام الحصالة الفوري والمحمي (5 جولد للإفراج والماء وسحب للبداية)
    async def on_room_tip(self, sender: User, tips: list[CurrencyItem]) -> None:
        for tip in tips:
            if tip.amount >= 5:
                sender_lower = sender.username.lower()
                if sender_lower in self.prisoners:
                    self.prisoners.remove(sender_lower)
                    await self.highrise.chat(f"💰 كفالة مقبولة! رشة ماء وإفراج عن @{sender.username} لخط البداية! 🌊🕊️")
                    
                    try: await self.highrise.send_emote("emote-wave", sender.id)
                    except: pass
                    await asyncio.sleep(1.0)
                    
                    if self.spawn_position:
                        await self.highrise.teleport(sender.id, self.spawn_position)
                        self.last_checked_positions[sender.id] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                        self.player_positions[sender.id] = self.spawn_position
                else:
                    await self.highrise.chat(f"❤️ شكراً @{sender.username} على دعم حصالة الغرفة بـ {tip.amount} جولد!")

    # 🔄 محرك توليد العشوائية اللامتناهية التامة والمصمم بناءً على طلبك بالملي متر:
    async def game_loop(self):
        try:
            while self.game_active:
                for uid, pos in self.player_positions.items():
                    if isinstance(pos, Position):
                        self.last_checked_positions[uid] = (round(pos.x, 1), round(pos.z, 1))

                # خطوة العشوائية التامة: يتم إنتاج نمط عشوائي حي في كل لفة من اللفات
                red_repeats = random.randint(1, 3) 
                
                # تنفيذ جولات الأحمر المتغير تلقائياً
                for _ in range(red_repeats):
                    if not self.game_active: break
                    self.light = "red"
                    alert_msg = random.choice([
                        "🔴 ضوء أحمر!!! تثبيت كامل! 🛑",
                        "🚨 تكرار مباغت للضوء الأحمر!!! ممنوع الحركة! 🛑",
                        "🛑 قف مكانك!!! ضوء أحمر، لا تتحرك! 🔴"
                    ])
                    await self.highrise.chat(alert_msg)
                    # وقت الأحمر العشوائي لكسر أي حفظ للتوقيت من قبل اللاعبين
                    await asyncio.sleep(random.uniform(2.5, 4.5))

                # يأتي الضوء الأخضر الأساسي
                if self.game_active:
                    self.light = "green"
                    await self.highrise.chat("🟢 ضوء أخضر! اركضوا نحو خط النهاية! 🏃‍♂️")
                    await asyncio.sleep(2.2) # ثانيتين و2 جزء من الثانية تماماً

                # 🎲 [فخ الأخضر المكرر العشوائي والمفاجئ] يزرع بنسبة 20% لمرة واحدة فقط طوال جولة اللعبة كاملة
                if self.game_active and not self.double_green_triggered and random.random() < 0.20:
                    self.double_green_triggered = True # حماية لمنع التكرار مرة أخرى في نفس اللعبة
                    self.light = "green"
                    await self.highrise.chat("⚡ فخ مباغت!!! ضوء أخضر مكرر فجأة وراء بعضه!!! اركضوا بسرعة! 🟢🟢")
                    await asyncio.sleep(2.2) # ثانيتين و2 جزء من الثانية تماماً

                await asyncio.sleep(0.5)
        except asyncio.CancelledError: pass

    async def on_chat(self, user: User, message: str) -> None:
        message_clean = message.strip().lower()
        username_lower = user.username.lower()

        if message_clean in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message_clean], user.id)
            except: pass
            return

        if username_lower == "qais29" or username_lower in self.moderators:
            pos = self.player_positions.get(user.id)
            
            if message_clean == "/setprison" and pos:
                self.prison_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🔒 تم تسجيل موقع السجن!")
            
            elif message_clean == "/setspawn" and pos:
                self.spawn_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🟩 تم تسجيل خط الانطلاق!")

            elif message_clean == "/setvip" and pos:
                self.vip_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("💎 تم تحديد منصة الـ VIP!")

            elif message_clean == "/setfinish" and pos:
                self.finish_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🏁 تم تسجيل خط النهاية (منطقة الأمان)!")

            # عند كتابة "ابدأ اللعبة" يتم تصفير كل شيء وبدء لعبة عشوائية غير مكررة نهائياً
            elif message_clean == "ابدأ اللعبة":
                if not self.game_active:
                    if not self.spawn_position or not self.finish_position or not self.prison_position:
                        await self.highrise.chat("⚠️ حدد كافة المواقع أولاً بالـ /set!")
                        return
                    
                    self.game_active = True
                    self.prisoners.clear() 
                    self.double_green_triggered = False # إعادة شحن وتجهيز فخ الأخضر المكرر العشوائي
                    await self.highrise.chat("🔄 لعبة جديدة كلياً وعشوائية تماماً! سحب الجميع لخط البداية... 🏁")
                    
                    try:
                        room_users = await self.highrise.get_room_users()
                        for room_user, pos_item in room_users.users:
                            await self.highrise.teleport(room_user.id, self.spawn_position)
                            self.last_checked_positions[room_user.id] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                            self.player_positions[room_user.id] = self.spawn_position
                    except: pass
                    
                    self.game_task = asyncio.create_task(self.game_loop())

            elif message_clean == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة بنجاح وتجميد الرصد.")

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
                                
                                await self.highrise.chat(f"👑 تم نقل @{room_user.username} إلى الـ VIP! 💎")
                                if self.vip_position:
                                    await self.highrise.teleport(room_user.id, self.vip_position)
                                    self.last_checked_positions[room_user.id] = (round(self.vip_position.x, 1), round(self.vip_position.z, 1))
                                player_found = True
                                break
                        if not player_found:
                            await self.highrise.chat("⚠️ لم يتم العثور على اللاعب المستهدف داخل الغرفة.")
                    except: pass
                else:
                    if username_lower in self.prisoners:
                        self.prisoners.remove(username_lower)
                    await self.highrise.chat(f"👑 تم نقل المسؤول @{user.username} فوراً إلى منصة الـ VIP! 💎")
                    if self.vip_position:
                        try:
                            await self.highrise.teleport(user.id, self.vip_position)
                            self.last_checked_positions[user.id] = (round(self.vip_position.x, 1), round(self.vip_position.z, 1))
                        except: pass

            elif message_clean.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم الإفراج اليدوي عن @{target_username}! جاري سحبه لنقطة البداية... 🌊")
                        
                        try:
                            room_users = await self.highrise.get_room_users()
                            for room_user, pos_item in room_users.users:
                                if room_user.username.lower() == target_username:
                                    if self.spawn_position:
                                        await self.highrise.teleport(room_user.id, self.spawn_position)
                                        self.last_checked_positions[room_user.id] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                                        self.player_positions[room_user.id] = self.spawn_position
                                    break
                        except: pass
                    else:
                        await self.highrise.chat("⚠️ هذا اللاعب ليس مسجوناً حالياً.")
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "ابدأ اللعبة", "اوقف اللعبة", "vip"]
            if message_clean in protected_commands or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذا الأمر مخصص حصرياً للإدارة والمشرفين!")
