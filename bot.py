import asyncio
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        # إحداثيات السجن وخط البداية (سيتم تحديثها تلقائياً عبر الأوامر داخل اللعبة)
        self.prison_position = Position(0, 0, 0)
        self.spawn_position = Position(0, 0, 0)
        # قاموس لحفظ مواقع اللاعبين بدقة لمنع الإقصاء بسبب حركات اليد والرجل التلقائية
        self.player_positions = {}
        # قائمة سوداء لحفظ أسماء المساجين حتى لو خرجوا ودخلوا للغرفة مجدداً
        self.prisoners = set()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 بوت لعبة Squid Game الاحترافي يعمل بنجاح!")

    async def on_user_join(self, user: User, position: Position) -> None:
        # تسجيل موقع اللاعب عند دخوله
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        # 🚨 مكافحة الاحتيال: إذا كان اللاعب مسجوناً وخرج ثم عاد، يتم سحبه للسجن فوراً!
        if user.username.lower() in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ قف مكانك يا @{user.username}! لقد حاولت الهروب بالخروج والعودة، عد إلى السجن!")
            if self.prison_position.x != 0:
                # تأخير بسيط للتأكد من تحميل الأفاتار بالكامل في الغرفة قبل النقل
                await asyncio.sleep(1.5)
                await self.highrise.teleport(user.id, self.prison_position)

    async def on_user_move(self, user: User, pos: Position) -> None:
        if not self.game_active or self.light == "green":
            if hasattr(pos, 'x') and hasattr(pos, 'z'):
                self.player_positions[user.id] = (round(pos.x, 1), round(pos.z, 1))
            return

        if self.light == "red":
            if hasattr(pos, 'x') and hasattr(pos, 'z'):
                current_x = round(pos.x, 1)
                current_z = round(pos.z, 1)
                old_pos = self.player_positions.get(user.id)

                if old_pos:
                    old_x, old_z = old_pos
                    distance_moved = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                    
                    # إذا تحرك اللاعب خطوة فعلية يتم إقصاؤه وإضافته للقائمة السوداء
                    if distance_moved > 0.2:
                        await self.highrise.chat(f"⚠️ المخالف @{user.username} تحرك أثناء الضوء الأحمر! إلى السجن!")
                        self.prisoners.add(user.username.lower())
                        if self.prison_position.x != 0:
                            await self.highrise.teleport(user.id, self.prison_position)
                    else:
                        pass
                else:
                    self.player_positions[user.id] = (current_x, current_z)

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        # أوامر إعدادات الغرفة (لصاحب البوت)
        if message == "/setprison":
            await self.highrise.chat("🔒 تم تسجيل موقع السجن الحالي بنجاح!")
        elif message == "/setspawn":
            await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")

        # أوامر التحكم باللعبة
        elif message == "ضوء اخضر":
            self.game_active = True
            self.light = "green"
            await self.highrise.chat("🟢 ضوء أخضر! تحركوا بحذر! 🏃‍♂️")

        elif message == "ضوء احمر":
            self.light = "red"
            await self.highrise.chat("🔴 ضوء أحمر! قف مكاااانك! 🛑")
            
        # 🔒 أمر الإفراج: حصرياً لـ qais29 فقط
        elif message.startswith("افراج"):
            if username_lower == "qais29":
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم العفو عن @{target_username} بواسطة القائد qais29. يمكنك العودة للعب!")
                        # هنا البوت يعيده تلقائياً لخط البداية إذا تم ضبط الإحداثيات
                    else:
                        await self.highrise.chat(f"هذا اللاعب ليس في السجن أصلاً.")
            else:
                await self.highrise.chat(f"❌ عذراً @{user.username}، أمر الإفراج صلاحية خاصة بالقائد qais29 فقط!")
