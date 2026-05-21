import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الأساسية بنظام نقي
        self.prison_position = None
        self.spawn_position = None
        self.vip_position = None
        self.finish_position = None
        self.bot_custom_position = None
        
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None

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
        print("🤖 بوت لعبة Squid Game الغدار والسينمائي جاهز للعمل على سيرفر رينار!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if isinstance(position, Position):
            self.player_positions[user.id] = position
        
        username_lower = user.username.lower()
        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الغرفة تحت تصرفك والعدالة جاهزة.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ عد إلى السجن يا @{user.username}!")
            if self.prison_position:
                await asyncio.sleep(2.0)
                await self.highrise.teleport(user.id, self.prison_position)
            return

    async def on_user_move(self, user: User, pos: Position) -> None:
        if isinstance(pos, Position):
            self.player_positions[user.id] = pos
        else:
            return

        username_lower = user.username.lower()
        if username_lower == "qais29" or not self.game_active:
            return

        current_x = round(pos.x, 1)
        current_z = round(pos.z, 1)

        # 1️⃣ فحص خط النهاية
        if self.finish_position and username_lower not in self.prisoners:
            if abs(pos.x - self.finish_position.x) < 1.0 and abs(pos.z - self.finish_position.z) < 1.0:
                await self.highrise.chat(f"🎉 مبروك للفائز الأسطوري @{user.username}! 🏆")
                if self.vip_position:
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        # 2️⃣ حماية الـ VIP
        if self.vip_position and username_lower not in self.prisoners:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5:
                await self.highrise.chat(f"🚨 تسلل مرفوض يا @{user.username}! إلى السجن!")
                self.prisoners.add(username_lower)
                try: await self.highrise.send_emote("emote-die", user.id)
                except: pass
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)
                return

        # 3️⃣ الرصد في الضوء الأحمر
        if self.light == "red":
            await self.highrise.chat(f"💥 لُقطت! المخالف @{user.username} تحرك في الأحمر! خذ هذه اللكمة! 🥊")
            self.prisoners.add(username_lower)
            try: await self.highrise.send_emote("emote-die", user.id)
            except: pass
            await asyncio.sleep(1.5)
            if self.prison_position:
                await self.highrise.teleport(user.id, self.prison_position)

    # 💰 الميزة الجديدة: دفع 5 جولد في الحصالة للخروج التلقائي من السجن
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        # التأكد من أن الهدية عبارة عن جولد (gold) وأن القيمة تساوي 5 أو أكثر
        if tip.type == "gold" and tip.amount >= 5:
            sender_lower = sender.username.lower()
            
            # فحص إذا كان الدافع مسجوناً بالفعل
            if sender_lower in self.prisoners:
                self.prisoners.remove(sender_lower)
                await self.highrise.chat(f"💰 دفع كفالة! تم الإفراج التلقائي عن @{sender.username} لإيداعه {tip.amount} جولد! 🕊️")
                
                # نقله فوراً إلى خط الانطلاق (Spawn) إذا كان محدداً
                if self.spawn_position:
                    await asyncio.sleep(0.5)
                    await self.highrise.teleport(sender.id, self.spawn_position)
            else:
                await self.highrise.chat(f"❤️ شكراً لك @{sender.username} على دعمك الكريم بـ {tip.amount} جولد! (أنت لست مسجوناً لتخرج)")

    async def game_loop(self):
        try:
            while self.game_active:
                self.light = "green"
                await self.highrise.chat(f"🟢 ضوء أخضر! تحركوا بسرعة! 🏃‍♂️")
                await asyncio.sleep(random.uniform(2.0, 4.5))
                
                if not self.game_active: break
                
                self.light = "red"
                await self.highrise.chat(f"🔴 ضوء أحمر!!! قف مكااااانك! 🛑")
                await asyncio.sleep(random.uniform(2.0, 5.0))
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        if message in self.dance_moves:
            try: await self.highrise.send_emote(self.dance_moves[message], user.id)
            except: pass
            return

        if username_lower == "qais29":
            pos = self.player_positions.get(user.id)
            
            if message == "/setprison" and pos:
                self.prison_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🔒 تم تسجيل موقع السجن بنجاح!")
            
            elif message == "/setspawn" and pos:
                self.spawn_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")

            elif message == "/setvip" and pos:
                self.vip_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("💎 تم تحديد منصة الـ VIP وحمايتها!")

            elif message == "/setfinish" and pos:
                self.finish_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان!")

            elif message == "/setbot" and pos:
                try:
                    self.bot_custom_position = Position(pos.x, pos.y, pos.z, "FrontRight")
                    bot_info = await self.highrise.get_bot_info()
                    await self.highrise.teleport(bot_info.user.id, self.bot_custom_position)
                    await asyncio.sleep(0.5)
                    await self.highrise.chat("🤖 تم تثبيت البوت بنجاح واستجاب للأمر دون أي اختفاء!")
                except Exception as e:
                    print(f"Error in setbot: {e}")
                    await self.highrise.chat("⚠️ حدث خطأ في خوادم اللعبة، جرب كتابة الأمر مرة أخرى.")

            elif message == "نسخ اللباس":
                try:
                    if user.outfit:
                        await self.highrise.set_outfit(user.outfit)
                        await self.highrise.chat("👕 تم نسخ لباسك بنجاح يا قائد!")
                except:
                    await self.highrise.chat("⚠️ تعذر قراءة خزانة الملابس.")

            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    bot_info = await self.highrise.get_bot_info()
                    if self.bot_custom_position:
                        await self.highrise.teleport(bot_info.user.id, self.bot_custom_position)
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 بدأت لعبة الحبار! نظام الأضواء نشط!")

            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة.")

            # 👮‍♂️ الحفاظ على الأمر القديم للإفراج اليدوي والمجاني بواسطة القائد قيس:
            elif message.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم العفو اليدوي عن @{target_username} بواسطة القائد قيس!")
                        if self.spawn_position:
                            # البحث عن آي دي المستخدم للإفراج عنه ونقله
                            for uid, upos in self.player_positions.items():
                                # (ملاحظة: النقل اليدوي يعتمد على تواجد اللاعب في الغرفة وحفظ موقعه)
                                pass
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في السجن أصلاً.")
                        
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "/setbot", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة"]
            if message in protected_commands or message.startswith("vip") or message.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الأوامر والامتيازات حصرية للقائد qais29!")
