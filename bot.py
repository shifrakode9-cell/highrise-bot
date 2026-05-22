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

        # قاموس الـ 10 رقصات بالأرقام
        self.dance_moves = {
            "1": "dance-tiktok8", "2": "dance-russian", "3": "dance-weird",
            "4": "dance-shoppingcart", "5": "dance-praise", "6": "emote-think",
            "7": "emote-wave", "8": "dance-blackpink", "9": "dance-drop", "10": "dance-handsup"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 نسخة الجولة الجديدة والتصفير الكامل جاهزة للعمل!")

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
            await self.highrise.chat(f"👮‍♂️ لا تحاول الهرب! عد إلى السجن يا @{user.username}!")
            if self.prison_position:
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"✨ أهلاً بك @{user.username} في اللعبة!")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not isinstance(pos, Position):
            return
            
        self.player_positions[user.id] = pos
        username_lower = user.username.lower()
        
        # القائد قيس فوق القوانين ومستثنى من أي رصد
        if username_lower == "qais29":
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)

        # 🏰 فحص هل اللاعب تجاوز خط النهاية ودخل منطقة الأمان؟
        is_inside_safe_zone = False
        if self.finish_position and current_z >= round(self.finish_position.z, 1) and abs(current_x - self.finish_position.x) < 7.5:
            is_inside_safe_zone = True

        # 🛑 [قانون السجن] في الأحمر على اللاعبين المتواجدين في الممر (قبل خط الأمان)
        if self.game_active and self.light == "red" and username_lower not in self.prisoners and not is_inside_safe_zone:
            old_pos = self.last_checked_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance = ((current_x - old_x)**2 + (current_z - old_z)**2)**0.5
                
                if distance > 0.18: # رصد الحركة المخالفة
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"💥 لُقطت! @{user.username} تحرك في الأحمر قبل خط الأمان! خذ لكمة السقوط! 🥊")
                    
                    try: await self.highrise.send_emote("emote-die", user.id)
                    except: pass
                    
                    await asyncio.sleep(2.0) # لقطة الموت والسقوط
                    
                    if self.prison_position:
                        await self.highrise.teleport(user.id, self.prison_position)
                        self.last_checked_positions[user.id] = (round(self.prison_position.x, 1), round(self.prison_position.z, 1))
                    return 

        # 🟢 [قانون الفوز الشرعي] ضوء أخضر + تخطي خط النهاية
        if self.game_active and self.light == "green" and is_inside_safe_zone and username_lower not in self.prisoners:
            await self.highrise.chat(f"🎉 مبروك الفوز الأسطوري @{user.username}! وصلت لخط الأمان ونقل للـ VIP! 🏆")
            if self.vip_position:
                await self.highrise.teleport(user.id, self.vip_position)
                self.last_checked_positions[user.id] = (round(self.vip_position.x, 1), round(self.vip_position.z, 1))
            return

        # 🔒 حماية منطقة الـ VIP من المتسللين يدوياً
        if self.vip_position and username_lower not in self.prisoners and not is_inside_safe_zone:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5:
                self.prisoners.add(username_lower)
                await self.highrise.chat(f"🚨 تسلل مرفوض إلى الـ VIP يا @{user.username}! إلى السجن! 🥊")
                try: await self.highrise.send_emote("emote-die", user.id)
                except: pass
                await asyncio.sleep(2.0) 
                if self.prison_position:
                    await self.highrise.teleport(user.id, self.prison_position)
                    self.last_checked_positions[user.id] = (round(self.prison_position.x, 1), round(self.prison_position.z, 1))
                return
            
        self.last_checked_positions[user.id] = (current_x, current_z)

    # 💰 نظام الحصالة (Room Tip Jar)
    async def on_room_tip(self, sender: User, tips: list[CurrencyItem]) -> None:
        for tip in tips:
            if tip.amount >= 5:
                sender_lower = sender.username.lower()
                if sender_lower in self.prisoners:
                    self.prisoners.remove(sender_lower)
                    await self.highrise.chat(f"💰 كفالة مقبولة! رشة ماء وإفراج عن @{sender.username} لخط البداية كلعبة جديدة! 🌊🕊️")
                    
                    try: await self.highrise.send_emote("emote-wave", sender.id)
                    except: pass
                    
                    if self.spawn_position:
                        await asyncio.sleep(0.5)
                        await self.highrise.teleport(sender.id, self.spawn_position)
                        self.last_checked_positions[sender.id] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                        self.player_positions[sender.id] = self.spawn_position
                else:
                    await self.highrise.chat(f"❤️ شكراً لك @{sender.username} على دعم حصالة الغرفة بـ {tip.amount} جولد!")

    # 🔄 نظام جولات الأضواء العشوائية والمباغتة
    async def game_loop(self):
        try:
            while self.game_active:
                for uid, pos in self.player_positions.items():
                    if isinstance(pos, Position):
                        self.last_checked_positions[uid] = (round(pos.x, 1), round(pos.z, 1))

                red_repeats = random.randint(1, 3) 
                green_repeats = random.choice([1, 2]) 
                
                pool = ["green"] * green_repeats + ["red"] * red_repeats
                random.shuffle(pool)

                for light_type in pool:
                    if not self.game_active: break

                    if light_type == "green":
                        self.light = "green"
                        await self.highrise.chat("🟢 ضوء أخضر! اركضوا نحو خط الأمان! 🏃‍♂️")
                        await asyncio.sleep(2.3) 
                    
                    elif light_type == "red":
                        self.light = "red"
                        alert_msg = random.choice([
                            "🔴 ضوء أحمر!!! قف مكانك تماماً! 🛑",
                            "🚨 تكرار الضوء الأحمر فجأة!!! ممنوع الحركة نهائياً! 🛑",
                            "🛑 تثبيت!!! ضوء أحمر مباغت، لا تتحرك! 🔴"
                        ])
                        await self.highrise.chat(alert_msg)
                        await asyncio.sleep(random.uniform(2.5, 4.5))

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

        # 👑 نظام التحكم والصلاحيات المطور والمشترك
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
                await self.highrise.chat("🏁 تم تسجيل خط النهاية (منطقة الأمان) بنجاح!")

            elif message_clean == "/setbot":
                await self.highrise.chat("🤖 البوت مستعد وفي الخدمة تماماً!")

            elif message_clean == "نسخ اللباس" and username_lower == "qais29":
                try:
                    if user.outfit:
                        await self.highrise.set_outfit(user.outfit)
                        await self.highrise.chat("👕 تم نسخ لباسك بنجاح يا قائد!")
                except: pass

            # 🔄 تعديل حاسم: تصفير كامل وعمل ريستارت جماعي للعبة وتطبيق القوانين على الكل!
            elif message_clean == "ابدأ اللعبة":
                if not self.game_active:
                    if not self.spawn_position or not self.finish_position or not self.prison_position:
                        await self.highrise.chat("⚠️ يرجى تحديد المواقع أولاً باوامر الـ /set!")
                        return
                    
                    self.game_active = True
                    
                    # 1️⃣ تصفير قائمة السجناء تماماً وعمل إفراج جماعي
                    self.prisoners.clear()
                    await self.highrise.chat("🔄 تصفير السجل وإفراج جماعي! جولة جديدة كلياً تبدأ الآن للجميع! 🏁")
                    
                    # 2️⃣ سحب كل الحاضرين في الغرفة تلقائياً ونقلهم لخط البداية لبدء التحدي سوياً
                    for uid, p_pos in list(self.player_positions.items()):
                        try:
                            await self.highrise.teleport(uid, self.spawn_position)
                            self.last_checked_positions[uid] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                        except:
                            pass
                    
                    # 3️⃣ تشغيل الرصد الذكي والجولات العلوية
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 انطلقت اللعبة! القوانين تطبق على الجميع دون استثناء! 🛑")

            elif message_clean == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة بنجاح وتجميد الرصد.")

            # 💎 نظام الـ VIP
            elif message_clean.startswith("vip"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    player_found = False
                    for uid, p_pos in self.player_positions.items():
                        try:
                            if target_username in self.prisoners:
                                self.prisoners.remove(target_username)
                            
                            await self.highrise.chat(f"👑 بأمر من الإدارة، تم نقل @{target_username} إلى الـ VIP! 💎")
                            if self.vip_position:
                                await self.highrise.teleport(uid, self.vip_position)
                                self.last_checked_positions[uid] = (round(self.vip_position.x, 1), round(self.vip_position.z, 1))
                            player_found = True
                            break
                        except: pass
                    if not player_found:
                        await self.highrise.chat(f"⚠️ تعذر العثور على اللاعب @{target_username}.")
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
                        await self.highrise.chat(f"🕊️ تم الإفراج اليدوي عن @{target_username}! 🌊")
                        for uid, p_pos in self.player_positions.items():
                            if self.spawn_position:
                                try:
                                    await self.highrise.teleport(uid, self.spawn_position)
                                    self.last_checked_positions[uid] = (round(self.spawn_position.x, 1), round(self.spawn_position.z, 1))
                                except: pass
                                return
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في السجن.")
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setbot", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة", "vip"]
            if message_clean in protected_commands or message_clean.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الصلاحيات القوية مخصصة للإدارة والمشرفين فقط!")
