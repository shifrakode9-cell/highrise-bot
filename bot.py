import asyncio
import random
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.light = "red"
        
        # إحداثيات المواقع الأساسية
        self.prison_position = Position(0, 0, 0)
        self.spawn_position = Position(0, 0, 0)
        self.vip_position = Position(0, 0, 0)
        self.finish_position = Position(0, 0, 0)
        
        # حفظ مواقع اللاعبين والمساجين
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None

        # قاموس الـ 10 رقصات
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
        print("🤖 بوت لعبة Squid Game الآلي جاهز للقيادة الذكية والمشاهد العشوائية!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        username_lower = user.username.lower()

        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الغرفة تحت تصرفك الآن.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ قف مكانك يا @{user.username}! لقد حاولت الهروب، عد إلى السجن!")
            if self.prison_position.x != 0:
                await asyncio.sleep(2.0)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"🤖 أهلاً بك @{user.username} في اللعبة.. تذكر: تحركك في الضوء الأحمر يعني نهايتك! 🛑")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if hasattr(pos, 'x') and hasattr(pos, 'z'):
            current_x = round(pos.x, 1)
            current_z = round(pos.z, 1)
        else:
            return

        username_lower = user.username.lower()

        if username_lower == "qais29":
            return

        # 1️⃣ فحص خط نهاية الأمان الأبيض بكامل العرض تلقائياً بناءً على اتجاه الممر في غرفتك
        if self.game_active and self.finish_position.x != 0 and username_lower not in self.prisoners:
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
                await self.highrise.chat(f"🎉 مبروك للفائز الأسطوري @{user.username}! لقد وصل إلى خط الأمان بنجاح! 🏆")
                if self.vip_position.x != 0:
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        # 2️⃣ حماية منطقة الـ VIP تلقائياً
        if self.vip_position.x != 0 and username_lower not in self.prisoners:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5:
                await self.highrise.chat(f"🚨 ممنوع الاحتيال يا @{user.username}! منطقة الـ VIP محظورة، إلى السجن!")
                self.prisoners.add(username_lower)
                if self.prison_position.x != 0:
                    await self.highrise.teleport(user.id, self.prison_position)
                return

        # مراقبة الحركة أثناء الضوء الأحمر
        if not self.game_active or self.light == "green":
            self.player_positions[user.id] = (current_x, current_z)
            return

        # 3️⃣ رصد المخالفين وتفعيل المشاهد العشوائية بمدة 3.5 ثانية
        if self.light == "red" and username_lower not in self.prisoners:
            old_pos = self.player_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance_moved = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                
                if distance_moved > 0.2:
                    self.prisoners.add(username_lower)
                    
                    # اختيار عشوائي بين 3 مشاهد تعبيرية للعقاب
                    scenario = random.choice(["dead", "drop", "sad"])
                    
                    if scenario == "dead":
                        await self.highrise.chat(f"⚠️ المخالف @{user.username} تحرك في الأحمر! تصفية فورية! 💀")
                        try:
                            await self.highrise.send_emote("emote-dead", user.id)
                        except:
                            pass
                    elif scenario == "drop":
                        await self.highrise.chat(f"⚠️ رصد حركة! @{user.username} ينهار ويسقط صريعاً! 🫨")
                        try:
                            await self.highrise.send_emote("dance-drop", user.id)
                        except:
                            pass
                    else:
                        await self.highrise.chat(f"⚠️ كشف المحاولة! @{user.username} يتحسر ويبكي قبل العقاب! 😭")
                        try:
                            await self.highrise.send_emote("emote-sad", user.id)
                        except:
                            pass
                    
                    # الانتظار لمدة 3 ثوانٍ ونصف تماماً لتمثيل المشهد السينمائي
                    await asyncio.sleep(3.5)
                    
                    if self.prison_position.x != 0:
                        await self.highrise.teleport(user.id, self.prison_position)
            else:
                self.player_positions[user.id] = (current_x, current_z)

    async def game_loop(self):
        try:
            while self.game_active:
                self.light = "green"
                await self.highrise.chat(f"🟢 ضوء أخضر! تحركوا بحذر! 🏃‍♂️")
                await asyncio.sleep(random.uniform(3.0, 6.0))
                
                if not self.game_active: break
                
                self.light = "red"
                await self.highrise.chat(f"🔴 ضوء أحمر! قف مكاااانك! 🛑")
                await asyncio.sleep(random.uniform(3.0, 5.0))
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        if message in self.dance_moves:
            try:
                # إرسال الـ user.id مع حركة الرقصة لتعمل بشكل سليم
                await self.highrise.send_emote(self.dance_moves[message], user.id)
            except Exception as e:
                print(f"Error dancing: {e}")
            return

        if username_lower == "qais29":
            if message == "/setprison":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تسجيل موقع السجن الحالي بنجاح!")
                        break
            
            elif message == "/setspawn":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.spawn_position = pos
                        await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")
                        break

            elif message == "/setvip":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.vip_position = pos
                        await self.highrise.chat("💎 تم تحديد منصة الـ VIP الخاصة بك وحمايتها!")
                        break

            elif message == "/setfinish":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.finish_position = pos
                        await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان بكامل العرض! البوت سيرصد أي لاعب يصل هنا.")
                        break

            elif message == "نسخ اللباس":
                try:
                    if user.outfit:
                        await self.highrise.set_outfit(user.outfit)
                        await self.highrise.chat("👕 تم نسخ لباسك وارتداؤه بنجاح يا قائد!")
                    else:
                        await self.highrise.chat("تعذر العثور على ملابس صالحة للنسخ حالياً.")
                except Exception as e:
                    print(f"Error copying outfit: {e}")
                    await self.highrise.chat("⚠️ عذراً يا قائد، واجهت مشكلة في قراءة خزانة الملابس.")

            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    
                    if self.finish_position.x != 0:
                        bot_info = await self.highrise.get_bot_info()
                        await self.highrise.teleport(bot_info.user.id, self.finish_position)
                    
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 تم تفعيل الإدارة الآلية! البوت يقف عند خط النهاية ومستعد للتحكيم.")

            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task:
                        self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة وإلغاء الإدارة التلقائية.")

            elif message.startswith("vip"):
                parts = message.split()
                if len(parts) > 1 and self.vip_position.x != 0:
                    target_username = parts[1].replace("@", "").lower()
                    room_users = await self.highrise.get_room_users()
                    found = False
                    for u, pos in room_users.content:
                        if u.username.lower() == target_username:
                            await self.highrise.teleport(u.id, self.vip_position)
                            await self.highrise.chat(f"👑 تم نقل الضيف @{u.username} إلى منصة الـ VIP بنجاح.")
                            found = True
                            break
                    if not found:
                        await self.highrise.chat("تعذر العثور على هذا اللاعب في الغرفة.")

            elif message.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم العفو عن @{target_username} والعودة للعب!")
                        if self.spawn_position.x != 0:
                            room_users = await self.highrise.get_room_users()
                            for u, pos in room_users.content:
                                if u.username.lower() == target_username:
                                    await self.highrise.teleport(u.id, self.spawn_position)
                                    break
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في السجن أصلاً.")
                        
        else:
            protected_commands = ["/setprison", "/setspawn", "/setvip", "/setfinish", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة"]
            if message in protected_commands or message.startswith("vip") or message.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الأوامر والامتيازات حصرية للقائد qais29!")

# ربط إيدي الغرفة والتوكن مباشرة لتسهيل التشغيل التلقائي على الـ Render
if __name__ == "__main__":
    room_id = "69fea9ea7ad83c6f1abffafe"
    api_token = "22b0110e1d415ec868f62fae55770b6b6c39edf1f02f8ec935e1741b2f61b2a5"
    
    from highrise.__main__ import *
    bot = MyBot()
    asyncio.run(bot.highrise.start(room_id, api_token))
