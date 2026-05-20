import os
import sys
import subprocess

# 📦 إجبار السيرفر على تحديث المكتبة للإصدار 25.1.0 لضمان عدم الطرد
try:
    import highrise
    if hasattr(highrise, '__version__') and not highrise.__version__.startswith('25'):
        raise ImportError
except ImportError:
    print("🔄 جاري تحديث مكتبة HighRise إلى الإصدار المستقر 25.1.0 إجبارياً...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "highrise-bot-sdk==25.1.0"])
    os.execv(sys.executable, ['python'] + sys.argv)

import asyncio
import random
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, CurrencyItem

# 🌐 سيرفر ويب مدمج للحفاظ على استقرار البوت 24 ساعة ومنع توقفه
class SimpleKeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("🤖 البوت يعمل بكفاءة ومستقر بالإصدار 25 المعتمد!".encode("utf-8"))
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

def run_keep_alive():
    try:
        server = HTTPServer(('0.0.0.0', 8080), SimpleKeepAliveServer)
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ تنبيه السيرفر المدمج: {e}")

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
        self.bot_fixed_position = Position(0, 0, 0)
        
        self.player_positions = {}
        self.prisoners = set()
        self.game_task = None

        # قائمة الـ 10 رقصات
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
        print("🤖 بوت لعبة Squid Game الاحترافي جاهز للعمل بكامل ميزاته بالإصدار 25 الجديد!")

    async def on_user_join(self, user: User, position: Position) -> None:
        if hasattr(position, 'x') and hasattr(position, 'z'):
            self.player_positions[user.id] = (round(position.x, 1), round(position.z, 1))
        
        username_lower = user.username.lower()

        if username_lower == "qais29":
            await self.highrise.chat(f"🫡 مرحباً بالقائد الأعلى @{user.username}! الترسانة الذكية والغرفة تحت تصرفك.")
            return

        if username_lower in self.prisoners:
            await self.highrise.chat(f"👮‍♂️ لا تحاول الهرب يا @{user.username}! عُد إلى السجن فوراً!")
            if self.prison_position.x != 0:
                await asyncio.sleep(2.0)
                await self.highrise.teleport(user.id, self.prison_position)
            return

        await self.highrise.chat(f"🤖 أهلاً بك @{user.username}.. احذر الغدر والأضواء العشوائية السريعة! 🛑")

    async def on_tip(self, sender: User, item: CurrencyItem, receiver: User) -> None:
        username_lower = sender.username.lower()
        if item.type == "gold":
            gold_amount = item.amount
            print(f"💰 تبرع جديد: اللاعب @{sender.username} دفع {gold_amount} جولد.")
            
            if gold_amount == 5:
                if username_lower in self.prisoners:
                    self.prisoners.remove(username_lower)
                    await self.highrise.chat(f"💸 كريم الغرفة الأسطوري @{sender.username} دفع 5 جولد دعم! تم العفو عنه وإعادته للعب فوراً! 🕊️")
                    if self.spawn_position.x != 0:
                        await asyncio.sleep(1.0)
                        await self.highrise.teleport(sender.id, self.spawn_position)
                else:
                    await self.highrise.chat(f"❤️ شكراً لك يا @{sender.username} على دعم الغرفة بـ 5 جولد!")
            else:
                await self.highrise.chat(f"💎 شكراً جزيلاً لـ @{sender.username} على تقديم دعم بقيمة {gold_amount} جولد للغرفة! 🔥")

    async def on_user_move(self, user: User, pos: Position) -> None:
        if hasattr(pos, 'x') and hasattr(pos, 'z'):
            current_x = round(pos.x, 1)
            current_z = round(pos.z, 1)
        else:
            return

        username_lower = user.username.lower()
        if username_lower == "qais29":
            return

        if self.game_active and self.finish_position.x != 0 and username_lower not in self.prisoners:
            distance_to_finish = ((current_x - self.finish_position.x)**2 + (current_z - self.finish_position.z)**2)**0.5
            if distance_to_finish < 1.2:
                await self.highrise.chat(f"🎉 مبروك للفائز المحترف @{user.username}! لقد عبرت المسافة بنجاح! 🏆")
                if self.vip_position.x != 0:
                    await self.highrise.teleport(user.id, self.vip_position)
                return

        if self.vip_position.x != 0 and username_lower not in self.prisoners:
            distance_to_vip = ((current_x - self.vip_position.x)**2 + (current_z - self.vip_position.z)**2)**0.5
            if distance_to_vip < 1.5:
                await self.highrise.chat(f"🚨 ممنوع الاحتيال يا @{user.username}! منطقة الـ VIP محظورة، إلى السجن!")
                self.prisoners.add(username_lower)
                await self.highrise.teleport(user.id, self.prison_position)
                return

        if not self.game_active or self.light == "green":
            self.player_positions[user.id] = (current_x, current_z)
            return

        if self.light == "red":
            old_pos = self.player_positions.get(user.id)
            if old_pos:
                old_x, old_z = old_pos
                distance_moved = ((current_x - old_x) ** 2 + (current_z - old_z) ** 2) ** 0.5
                
                if distance_moved > 0.2:
                    self.prisoners.add(username_lower)
                    await self.highrise.chat(f"🚨🚨 المخالف @{user.username} تحرك في الأحمر! تصفية فورية! 💥🥊")
                    try:
                        await self.highrise.send_emote("emote-superpunch")
                    except:
                        try: await self.highrise.send_emote("emote-punch")
                        except: pass
                    try:
                        await self.highrise.send_emote("dance-drop", user.id)
                    except:
                        pass
                    await asyncio.sleep(1.0)
                    if self.prison_position.x != 0:
                        await self.highrise.teleport(user.id, self.prison_position)
            else:
                self.player_positions[user.id] = (current_x, current_z)

    async def game_loop(self):
        try:
            while self.game_active:
                self.light = "green"
                await self.highrise.chat("🟢 ضوء أخضر! تحركوا بسرعة وبحذر! 🏃‍♂️")
                await asyncio.sleep(3.0)
                if not self.game_active: break
                
                self.light = "red"
                await self.highrise.chat("🔴 ضوء أحمر! قف مكاااانك! 🛑")
                await asyncio.sleep(random.uniform(2.0, 4.5))
                if not self.game_active: break
                
                if random.random() < 0.40:
                    self.light = "red"
                    await self.highrise.chat("🚨 خددددعة! أحمر مجدداً! قف مكانك لا تتحرك! 🔴🛑")
                    await asyncio.sleep(random.uniform(1.5, 3.5))
        except asyncio.CancelledError:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        if message in self.dance_moves:
            try:
                await self.highrise.send_emote(self.dance_moves[message])
            except Exception as e:
                print(f"Error dancing: {e}")
            return

        if username_lower == "qais29":
            if message == "/setbotpos":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.bot_fixed_position = Position(pos.x, pos.y, pos.z, pos.facing)
                        bot_info = await self.highrise.get_bot_info()
                        await self.highrise.teleport(bot_info.user.id, self.bot_fixed_position)
                        await self.highrise.chat("🤖 تم تثبيت موقع وقوف البوت بنجاح!")
                        break

            elif message == "/setprison":
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
                        await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان للتحكيم التلقائي.")
                        break

            elif message == "نسخ اللباس":
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.username.lower() == "qais29":
                            await self.highrise.set_outfit(u.outfit)
                            await self.highrise.chat("👕 تم نسخ لباسك وارتداؤه بنجاح يا قائد!")
                            break
                except Exception as e:
                    print(f"Error copying outfit: {e}")
                    await self.highrise.chat("⚠️ واجهت مشكلة في قراءة خزانة الملابس.")

            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 تم تفعيل الإدارة الآلية! البوت مستعد للمراقبة والتحكيم.")

            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task: self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة بنجاح.")

            elif message.startswith("vip"):
                parts = message.split()
                if len(parts) == 1 and self.vip_position.x != 0:
                    await self.highrise.teleport(user.id, self.vip_position)
                    await self.highrise.chat(f"👑 مرحباً بك في منصتك الخاصة يا قائد @{user.username}!")
                elif len(parts) > 1 and self.vip_position.x != 0:
                    target_username = parts[1].replace("@", "").lower()
                    room_users = await self.highrise.get_room_users()
                    found = False
                    for u, pos in room_users.content:
                        if u.username.lower() == target_username:
                            await self.highrise.teleport(u.id, self.vip_position)
                            await self.highrise.chat(f"👑 تم نقل الضيف @{u.username} إلى منصة الـ VIP بنجاح.")
                            found = True
                            break
                    if not found: await self.highrise.chat("تعذر العثور على هذا اللاعب في الغرفة.")

            elif message.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ تم العفو اليدوي عن @{target_username} والعودة للعب!")
                        if self.spawn_position.x != 0:
                            room_users = await self.highrise.get_room_users()
                            for u, pos in room_users.content:
                                if u.username.lower() == target_username:
                                    await self.highrise.teleport(u.id, self.spawn_position)
                                    break
                    else: await self.highrise.chat("هذا اللاعب ليس في قائمة المساجين حالياً.")
        else:
            protected_commands =
